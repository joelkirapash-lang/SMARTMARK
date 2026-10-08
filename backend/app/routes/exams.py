from flask import Blueprint, g, jsonify, request

from app.extensions import db
from app.models import Exam, Role
from app.utils.auth import require_auth, require_role, scoped
from app.utils.audit import log_action

bp = Blueprint("exams", __name__, url_prefix="/api")

ADMIN = Role.SCHOOL_ADMIN.value


@bp.get("/exams")
@require_auth
def list_exams():
    exams = scoped(Exam).order_by(Exam.created_at.desc()).all()
    return jsonify([e.to_dict() for e in exams])


@bp.post("/exams")
@require_role(ADMIN)
def create_exam():
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400
    exam = Exam(
        school_id=g.school_id,
        name=name,
        term=data.get("term"),
        created_by_user_id=g.current_user.id,
    )
    db.session.add(exam)
    log_action(g.school_id, g.current_user.id, "EXAM_CREATED", "exam", exam.id, {"name": name})
    db.session.commit()
    return jsonify(exam.to_dict()), 201


@bp.post("/exams/<exam_id>/publish")
@require_role(ADMIN)
def publish_exam(exam_id):
    exam = scoped(Exam).filter_by(id=exam_id).first()
    if exam is None:
        return jsonify({"error": "Not found"}), 404
    exam.is_published = True
    log_action(g.school_id, g.current_user.id, "EXAM_PUBLISHED", "exam", exam.id)
    db.session.commit()
    return jsonify(exam.to_dict())
