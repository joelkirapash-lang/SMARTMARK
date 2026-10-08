import csv
import io
from datetime import datetime

from flask import Blueprint, g, jsonify, request

from app.extensions import db
from app.models import User, Role, UserStatus, Grade, Stream, TeacherAssignment, Invitation
from app.utils.auth import require_auth, require_role, scoped
from app.utils.identity import generate_smartmark_email
from app.utils.audit import log_action

bp = Blueprint("users", __name__, url_prefix="/api")

ADMIN = Role.SCHOOL_ADMIN.value
TEACHER_ROLES = [Role.TEACHER.value, Role.EDUCATOR.value]


@bp.get("/teachers")
@require_role(ADMIN)
def list_teachers():
    teachers = scoped(User).filter(User.role.in_([Role.TEACHER, Role.EDUCATOR])).order_by(User.first_name).all()
    return jsonify([t.to_dict() for t in teachers])


@bp.get("/students")
@require_auth
def list_students():
    q = scoped(User).filter_by(role=Role.STUDENT, is_archived=False)
    grade_id = request.args.get("grade_id")
    stream_id = request.args.get("stream_id")
    search = request.args.get("search")

    # Teachers only see students in classes they are authorized for.
    if g.role in TEACHER_ROLES:
        allowed_grade_ids = _teacher_allowed_grade_ids(g.current_user)
        q = q.filter(User.grade_id.in_(allowed_grade_ids)) if allowed_grade_ids else q.filter(False)

    if grade_id:
        q = q.filter_by(grade_id=grade_id)
    if stream_id:
        q = q.filter_by(stream_id=stream_id)
    if search:
        like = f"%{search.lower()}%"
        q = q.filter(
            db.or_(
                db.func.lower(User.first_name).like(like),
                db.func.lower(User.second_name).like(like),
                db.func.lower(User.admission_number).like(like),
            )
        )
    students = q.order_by(User.first_name).all()
    return jsonify([s.to_dict() for s in students])


def _teacher_allowed_grade_ids(teacher: User):
    ids = set()
    if teacher.home_grade_id:
        ids.add(teacher.home_grade_id)
    assignments = TeacherAssignment.query.filter_by(teacher_id=teacher.id).all()
    for a in assignments:
        ids.add(a.grade_id)
    return list(ids)


@bp.post("/students/bulk-import")
@require_role(ADMIN)
def bulk_import_students():
    """
    CSV bulk import. Expected columns:
    first_name,second_name,other_name,admission_number,gender,date_of_birth,
    personal_email,phone_number,grade_id,stream_id,guardian_name,guardian_phone,guardian_email

    This creates INVITED student accounts directly (no invitation email is
    triggered here - that's a separate, explicit step per the invitation
    workflow) so an admin can bulk-load a whole class roster at once.
    """
    if "file" not in request.files:
        return jsonify({"error": "CSV file is required (field name 'file')"}), 400

    raw = request.files["file"].read().decode("utf-8-sig")
    reader = csv.DictReader(io.StringIO(raw))

    created, errors = [], []
    for i, row in enumerate(reader, start=2):  # row 1 is the header
        try:
            first_name = (row.get("first_name") or "").strip()
            if not first_name:
                errors.append({"row": i, "error": "first_name is required"})
                continue
            second_name = (row.get("second_name") or "").strip()
            smartmark_email = generate_smartmark_email(
                _school_slug(), first_name, second_name, Role.STUDENT.value
            )
            dob_raw = (row.get("date_of_birth") or "").strip()
            student = User(
                school_id=g.school_id,
                role=Role.STUDENT,
                first_name=first_name,
                second_name=second_name,
                other_name=(row.get("other_name") or "").strip(),
                admission_number=(row.get("admission_number") or "").strip(),
                gender=(row.get("gender") or "").strip(),
                date_of_birth=datetime.strptime(dob_raw, "%Y-%m-%d").date() if dob_raw else None,
                personal_email=(row.get("personal_email") or "").strip().lower(),
                phone_number=(row.get("phone_number") or "").strip(),
                grade_id=(row.get("grade_id") or "").strip() or None,
                stream_id=(row.get("stream_id") or "").strip() or None,
                guardian_name=(row.get("guardian_name") or "").strip(),
                guardian_phone=(row.get("guardian_phone") or "").strip(),
                guardian_email=(row.get("guardian_email") or "").strip().lower(),
                smartmark_email=smartmark_email,
                status=UserStatus.INVITED,
            )
            db.session.add(student)
            db.session.flush()
            created.append(student.to_dict())
        except Exception as e:  # keep importing the rest of the rows
            errors.append({"row": i, "error": str(e)})

    log_action(g.school_id, g.current_user.id, "STUDENTS_BULK_IMPORTED", meta={"count": len(created)})
    db.session.commit()
    return jsonify({"created": created, "errors": errors}), 201


def _school_slug():
    from app.models import School
    return School.query.get(g.school_id).slug


@bp.put("/teachers/<teacher_id>/assignments")
@require_role(ADMIN)
def set_teacher_assignments(teacher_id):
    """Admin sets a teacher's authorized grade/stream/subject combinations.
    Teachers can never modify their own assignments (no route exists for
    that under the teacher role)."""
    teacher = scoped(User).filter(User.id == teacher_id, User.role.in_([Role.TEACHER, Role.EDUCATOR])).first()
    if teacher is None:
        return jsonify({"error": "Not found"}), 404

    data = request.get_json(force=True) or {}
    assignments = data.get("assignments", [])

    TeacherAssignment.query.filter_by(teacher_id=teacher.id, school_id=g.school_id).delete()
    created = []
    for a in assignments:
        ta = TeacherAssignment(
            school_id=g.school_id,
            teacher_id=teacher.id,
            grade_id=a.get("grade_id"),
            stream_id=a.get("stream_id"),
            subject_id=a.get("subject_id"),
        )
        db.session.add(ta)
        created.append(ta)

    log_action(g.school_id, g.current_user.id, "TEACHER_ASSIGNMENTS_UPDATED", "user", teacher.id)
    db.session.commit()
    return jsonify([a.to_dict() for a in created])


@bp.get("/teachers/<teacher_id>/assignments")
@require_role(ADMIN)
def get_teacher_assignments(teacher_id):
    assignments = TeacherAssignment.query.filter_by(teacher_id=teacher_id, school_id=g.school_id).all()
    return jsonify([a.to_dict() for a in assignments])


@bp.post("/students/promote")
@require_role(ADMIN)
def promote_students():
    """Year-end bulk promotion: move students from one grade/stream to the
    next, archiving the prior class snapshot via the audit log. Students at
    the terminal grade are archived (graduated) instead of promoted."""
    data = request.get_json(force=True) or {}
    mapping = data.get("mapping", [])  # [{from_grade_id, from_stream_id, to_grade_id, to_stream_id}]
    graduate_grade_id = data.get("graduate_grade_id")  # students here get archived, not moved

    moved, graduated = 0, 0
    for m in mapping:
        q = scoped(User).filter_by(role=Role.STUDENT, grade_id=m["from_grade_id"], is_archived=False)
        if m.get("from_stream_id"):
            q = q.filter_by(stream_id=m["from_stream_id"])
        students = q.all()
        for s in students:
            if m.get("from_grade_id") == graduate_grade_id:
                s.is_archived = True
                graduated += 1
            else:
                s.grade_id = m["to_grade_id"]
                s.stream_id = m.get("to_stream_id")
                moved += 1

    log_action(g.school_id, g.current_user.id, "STUDENTS_PROMOTED", meta={"moved": moved, "graduated": graduated})
    db.session.commit()
    return jsonify({"moved": moved, "graduated": graduated})
