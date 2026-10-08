from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, g, jsonify, request

from app.extensions import db
from app.models import User, Exam, Mark, Subject, PerformanceBand, Role, School, ReportShareLink
from app.utils.auth import require_auth, require_role, scoped
from app.utils.security import generate_secure_token, hash_token
from app.routes.academics import resolve_band
from app.routes.marks import _authorize_class_access

bp = Blueprint("reports", __name__, url_prefix="/api")


def _build_report_card(school: School, student: User, exam: Exam):
    marks = Mark.query.filter_by(school_id=school.id, exam_id=exam.id, student_id=student.id).all()
    subjects = {s.id: s for s in Subject.query.filter_by(school_id=school.id).all()}
    bands = PerformanceBand.query.filter_by(school_id=school.id).order_by(PerformanceBand.min_score).all()

    subject_rows = []
    total, count = 0, 0
    for m in marks:
        band = resolve_band(bands, m.score)
        if m.score is not None:
            total += m.score
            count += 1
        subject_rows.append({
            "subject": subjects[m.subject_id].name if m.subject_id in subjects else "Unknown",
            "score": m.score,
            "max_score": m.max_score,
            "band": band.code if band else None,
            "band_label": band.label if band else None,
            "remark": m.remark,
        })

    return {
        "school": {
            "name": school.name,
            "motto": school.motto,
            "crest_url": school.crest_url,
            "address": school.address,
            "footer": school.report_card_footer,
        },
        "student": {
            "name": student.full_name(),
            "admission_number": student.admission_number,
            "grade_id": student.grade_id,
            "stream_id": student.stream_id,
            "photo_url": student.photo_url,
        },
        "exam": {"name": exam.name, "term": exam.term},
        "subjects": subject_rows,
        "total": total,
        "average": round(total / count, 2) if count else None,
    }


@bp.get("/reports/card")
@require_auth
def get_report_card():
    student_id = request.args.get("student_id")
    exam_id = request.args.get("exam_id")
    if not student_id or not exam_id:
        return jsonify({"error": "student_id and exam_id are required"}), 400

    student = scoped(User).filter_by(id=student_id, role=Role.STUDENT).first()
    exam = scoped(Exam).filter_by(id=exam_id).first()
    if student is None or exam is None:
        return jsonify({"error": "Not found"}), 404

    if g.role == Role.STUDENT.value and g.current_user.id != student_id:
        return jsonify({"error": "Forbidden"}), 403
    if g.role in [Role.TEACHER.value, Role.EDUCATOR.value]:
        if not _authorize_class_access(student.grade_id, student.stream_id):
            return jsonify({"error": "Forbidden"}), 403

    school = School.query.get(g.school_id)
    return jsonify(_build_report_card(school, student, exam))


@bp.post("/reports/share-link")
@require_role(Role.SCHOOL_ADMIN.value)
def create_share_link():
    """Admin generates a token-based, no-login link a parent can use to view
    one student's report card for one published exam."""
    data = request.get_json(force=True) or {}
    student_id = data.get("student_id")
    exam_id = data.get("exam_id")

    student = scoped(User).filter_by(id=student_id, role=Role.STUDENT).first()
    exam = scoped(Exam).filter_by(id=exam_id).first()
    if student is None or exam is None:
        return jsonify({"error": "Invalid student_id or exam_id"}), 400
    if not exam.is_published:
        return jsonify({"error": "Exam must be published before sharing report cards"}), 400

    raw_token = generate_secure_token()
    link = ReportShareLink(
        school_id=g.school_id,
        student_id=student_id,
        exam_id=exam_id,
        token_hash=hash_token(raw_token),
        expires_at=datetime.now(timezone.utc) + timedelta(days=30),
    )
    db.session.add(link)
    db.session.commit()

    base = current_app.config["FRONTEND_BASE_URL"].rstrip("/")
    return jsonify({"url": f"{base}/report/{raw_token}", "expires_at": link.expires_at.isoformat()}), 201


@bp.get("/reports/shared/<raw_token>")
def get_shared_report(raw_token):
    """Public - no login required. Only exposes the one report card the
    token was issued for."""
    link = ReportShareLink.query.filter_by(token_hash=hash_token(raw_token), revoked=False).first()
    if link is None:
        return jsonify({"error": "This link is invalid or no longer available."}), 404
    if link.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        return jsonify({"error": "This link has expired."}), 404

    school = School.query.get(link.school_id)
    student = User.query.get(link.student_id)
    exam = Exam.query.get(link.exam_id)
    if not (school and student and exam):
        return jsonify({"error": "This link is invalid or no longer available."}), 404

    return jsonify(_build_report_card(school, student, exam))
