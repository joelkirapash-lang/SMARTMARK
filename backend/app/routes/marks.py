import io

from flask import Blueprint, g, jsonify, request, send_file
from openpyxl import Workbook

from app.extensions import db
from app.models import Mark, Exam, Subject, User, Role, TeacherAssignment, PerformanceBand
from app.utils.auth import require_auth, require_role, scoped
from app.utils.audit import log_action
from app.routes.academics import resolve_band

bp = Blueprint("marks", __name__, url_prefix="/api")

TEACHER_ROLES = [Role.TEACHER, Role.EDUCATOR]


def is_teacher_authorized(teacher: User, grade_id: str, stream_id: str, subject_id: str) -> bool:
    """Server-side enforcement - never trust the frontend. A teacher may
    edit marks only for grade/stream/subject combinations an admin
    explicitly assigned to them (their home class counts as an assignment
    too, checked separately by the caller if desired)."""
    if teacher.home_grade_id == grade_id and (
        teacher.home_stream_id is None or teacher.home_stream_id == stream_id
    ):
        # Home class - still require the subject to be one of their assignments
        pass
    assignments = TeacherAssignment.query.filter_by(teacher_id=teacher.id, school_id=teacher.school_id).all()
    for a in assignments:
        if a.grade_id == grade_id and a.subject_id == subject_id and (
            a.stream_id is None or a.stream_id == stream_id
        ):
            return True
    return False


def _authorize_class_access(grade_id, stream_id, subject_id=None):
    """Raises via return of (ok, error_response)."""
    if g.role in [Role.TEACHER.value, Role.EDUCATOR.value]:
        if subject_id is None or not is_teacher_authorized(g.current_user, grade_id, stream_id, subject_id):
            return False
    return True


@bp.get("/marks/grid")
@require_auth
def get_marks_grid():
    """Returns the editable score grid for Grade -> Stream -> Exam -> Subject."""
    exam_id = request.args.get("exam_id")
    grade_id = request.args.get("grade_id")
    stream_id = request.args.get("stream_id")
    subject_id = request.args.get("subject_id")

    if not all([exam_id, grade_id, subject_id]):
        return jsonify({"error": "exam_id, grade_id and subject_id are required"}), 400

    if not _authorize_class_access(grade_id, stream_id, subject_id):
        return jsonify({"error": "Forbidden: not authorized for this class/subject"}), 403

    q = scoped(User).filter_by(role=Role.STUDENT, grade_id=grade_id, is_archived=False)
    if stream_id:
        q = q.filter_by(stream_id=stream_id)
    students = q.order_by(User.first_name).all()

    existing = {
        m.student_id: m
        for m in scoped(Mark).filter_by(exam_id=exam_id, subject_id=subject_id).all()
    }

    rows = []
    for s in students:
        mark = existing.get(s.id)
        rows.append({
            "student_id": s.id,
            "student_name": s.full_name(),
            "admission_number": s.admission_number,
            "score": mark.score if mark else None,
            "max_score": mark.max_score if mark else 100,
            "remark": mark.remark if mark else None,
        })
    return jsonify({"rows": rows})


@bp.post("/marks/grid")
@require_auth
def save_marks_grid():
    """Bulk upsert of the score grid - supports pasting a full column of
    scores from Excel (the frontend sends the parsed rows)."""
    data = request.get_json(force=True) or {}
    exam_id = data.get("exam_id")
    grade_id = data.get("grade_id")
    stream_id = data.get("stream_id")
    subject_id = data.get("subject_id")
    rows = data.get("rows", [])

    if not all([exam_id, grade_id, subject_id]):
        return jsonify({"error": "exam_id, grade_id and subject_id are required"}), 400

    if not _authorize_class_access(grade_id, stream_id, subject_id):
        return jsonify({"error": "Forbidden: not authorized for this class/subject"}), 403

    saved = 0
    validation_errors = []
    for row in rows:
        student_id = row.get("student_id")
        score = row.get("score")
        max_score = row.get("max_score", 100)

        # Confirm the student actually belongs to this school/class.
        student = scoped(User).filter_by(id=student_id, role=Role.STUDENT, grade_id=grade_id).first()
        if student is None:
            validation_errors.append({"student_id": student_id, "error": "Student not found in this class"})
            continue

        if score is not None:
            try:
                score = float(score)
            except (TypeError, ValueError):
                validation_errors.append({"student_id": student_id, "error": "Score must be numeric"})
                continue
            if score < 0 or score > float(max_score):
                validation_errors.append({"student_id": student_id, "error": f"Score must be between 0 and {max_score}"})
                continue

        mark = scoped(Mark).filter_by(exam_id=exam_id, student_id=student_id, subject_id=subject_id).first()
        if mark is None:
            mark = Mark(
                school_id=g.school_id,
                exam_id=exam_id,
                student_id=student_id,
                subject_id=subject_id,
                grade_id=grade_id,
                stream_id=stream_id,
                entered_by_user_id=g.current_user.id,
            )
            db.session.add(mark)
        mark.score = score
        mark.max_score = max_score
        mark.remark = row.get("remark")
        mark.entered_by_user_id = g.current_user.id
        saved += 1

    log_action(g.school_id, g.current_user.id, "MARKS_SAVED", "exam", exam_id, {"subject_id": subject_id, "count": saved})
    db.session.commit()
    return jsonify({"saved": saved, "errors": validation_errors})


@bp.get("/marklist")
@require_auth
def get_marklist():
    """Ranked class marklist per Grade/Stream/Exam across all subjects."""
    exam_id = request.args.get("exam_id")
    grade_id = request.args.get("grade_id")
    stream_id = request.args.get("stream_id")

    if not all([exam_id, grade_id]):
        return jsonify({"error": "exam_id and grade_id are required"}), 400

    if g.role in [Role.TEACHER.value, Role.EDUCATOR.value]:
        allowed = (g.current_user.home_grade_id == grade_id) or TeacherAssignment.query.filter_by(
            teacher_id=g.current_user.id, grade_id=grade_id
        ).first() is not None
        if not allowed:
            return jsonify({"error": "Forbidden"}), 403

    q = scoped(User).filter_by(role=Role.STUDENT, grade_id=grade_id, is_archived=False)
    if stream_id:
        q = q.filter_by(stream_id=stream_id)
    students = q.all()

    subjects = {s.id: s for s in scoped(Subject).all()}
    bands = scoped(PerformanceBand).order_by(PerformanceBand.min_score).all()

    marks = scoped(Mark).filter_by(exam_id=exam_id, grade_id=grade_id).all()
    by_student = {}
    for m in marks:
        by_student.setdefault(m.student_id, []).append(m)

    results = []
    for s in students:
        student_marks = by_student.get(s.id, [])
        total = sum(m.score for m in student_marks if m.score is not None)
        count = sum(1 for m in student_marks if m.score is not None)
        average = round(total / count, 2) if count else None
        subject_breakdown = [
            {
                "subject_id": m.subject_id,
                "subject_name": subjects[m.subject_id].name if m.subject_id in subjects else None,
                "score": m.score,
                "band": (resolve_band(bands, m.score).code if resolve_band(bands, m.score) else None),
            }
            for m in student_marks
        ]
        results.append({
            "student_id": s.id,
            "student_name": s.full_name(),
            "admission_number": s.admission_number,
            "total": total,
            "average": average,
            "subjects": subject_breakdown,
        })

    # Rank by average, highest first; students with no marks rank last.
    results.sort(key=lambda r: (r["average"] is None, -(r["average"] or 0)))
    for i, r in enumerate(results, start=1):
        r["position"] = i

    return jsonify({"marklist": results})


@bp.get("/marklist/export")
@require_auth
def export_marklist_excel():
    exam_id = request.args.get("exam_id")
    grade_id = request.args.get("grade_id")
    stream_id = request.args.get("stream_id")

    # Re-use the same computation as the JSON endpoint.
    resp = get_marklist()
    if isinstance(resp, tuple):
        return resp  # an error response (e.g. 403) - pass it straight through
    payload = resp.get_json()
    marklist = payload["marklist"]

    wb = Workbook()
    ws = wb.active
    ws.title = "Marklist"
    ws.append(["Position", "Admission No.", "Student Name", "Total", "Average"])
    for row in marklist:
        ws.append([row["position"], row["admission_number"], row["student_name"], row["total"], row["average"]])

    buffer = io.BytesIO()
    wb.save(buffer)
    buffer.seek(0)
    return send_file(
        buffer,
        as_attachment=True,
        download_name="marklist.xlsx",
        mimetype="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
    )
