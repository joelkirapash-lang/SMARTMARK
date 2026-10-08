from flask import Blueprint, g, jsonify, request

from app.extensions import db
from app.models import Grade, Stream, Subject, GradeSubject, PerformanceBand, Role
from app.utils.auth import require_auth, require_role, scoped
from app.utils.audit import log_action

bp = Blueprint("academics", __name__, url_prefix="/api")

ADMIN = Role.SCHOOL_ADMIN.value


# ---------- Grades ----------
@bp.get("/grades")
@require_auth
def list_grades():
    grades = scoped(Grade).filter_by(is_archived=False).order_by(Grade.order_index).all()
    return jsonify([g_.to_dict() for g_ in grades])


@bp.post("/grades")
@require_role(ADMIN)
def create_grade():
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    if not name:
        return jsonify({"error": "name is required"}), 400
    grade = Grade(school_id=g.school_id, name=name, order_index=data.get("order_index", 0))
    db.session.add(grade)
    log_action(g.school_id, g.current_user.id, "GRADE_CREATED", "grade", grade.id, {"name": name})
    db.session.commit()
    return jsonify(grade.to_dict()), 201


@bp.delete("/grades/<grade_id>")
@require_role(ADMIN)
def archive_grade(grade_id):
    grade = scoped(Grade).filter_by(id=grade_id).first()
    if grade is None:
        return jsonify({"error": "Not found"}), 404
    grade.is_archived = True
    log_action(g.school_id, g.current_user.id, "GRADE_ARCHIVED", "grade", grade.id)
    db.session.commit()
    return jsonify({"ok": True})


# ---------- Streams ----------
@bp.get("/streams")
@require_auth
def list_streams():
    q = scoped(Stream)
    grade_id = request.args.get("grade_id")
    if grade_id:
        q = q.filter_by(grade_id=grade_id)
    return jsonify([s.to_dict() for s in q.all()])


@bp.post("/streams")
@require_role(ADMIN)
def create_stream():
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    grade_id = data.get("grade_id")
    if not name or not grade_id:
        return jsonify({"error": "name and grade_id are required"}), 400
    grade = scoped(Grade).filter_by(id=grade_id).first()
    if grade is None:
        return jsonify({"error": "Invalid grade_id"}), 400
    stream = Stream(school_id=g.school_id, grade_id=grade_id, name=name)
    db.session.add(stream)
    log_action(g.school_id, g.current_user.id, "STREAM_CREATED", "stream", stream.id, {"name": name})
    db.session.commit()
    return jsonify(stream.to_dict()), 201


# ---------- Subjects ----------
@bp.get("/subjects")
@require_auth
def list_subjects():
    return jsonify([s.to_dict() for s in scoped(Subject).all()])


@bp.post("/subjects")
@require_role(ADMIN)
def create_subject():
    data = request.get_json(force=True) or {}
    name = (data.get("name") or "").strip()
    code = (data.get("code") or "").strip().upper()
    if not name or not code:
        return jsonify({"error": "name and code are required"}), 400
    subject = Subject(school_id=g.school_id, name=name, code=code)
    db.session.add(subject)
    log_action(g.school_id, g.current_user.id, "SUBJECT_CREATED", "subject", subject.id, {"name": name})
    db.session.commit()
    return jsonify(subject.to_dict()), 201


@bp.post("/grades/<grade_id>/subjects")
@require_role(ADMIN)
def assign_subject_to_grade(grade_id):
    data = request.get_json(force=True) or {}
    subject_id = data.get("subject_id")
    grade = scoped(Grade).filter_by(id=grade_id).first()
    subject = scoped(Subject).filter_by(id=subject_id).first()
    if grade is None or subject is None:
        return jsonify({"error": "Invalid grade_id or subject_id"}), 400
    existing = GradeSubject.query.filter_by(grade_id=grade_id, subject_id=subject_id).first()
    if existing:
        return jsonify({"error": "Already assigned"}), 400
    gs = GradeSubject(school_id=g.school_id, grade_id=grade_id, subject_id=subject_id)
    db.session.add(gs)
    db.session.commit()
    return jsonify({"ok": True}), 201


@bp.get("/grades/<grade_id>/subjects")
@require_auth
def list_grade_subjects(grade_id):
    rows = GradeSubject.query.filter_by(school_id=g.school_id, grade_id=grade_id).all()
    subject_ids = [r.subject_id for r in rows]
    subjects = Subject.query.filter(Subject.id.in_(subject_ids)).all() if subject_ids else []
    return jsonify([s.to_dict() for s in subjects])


# ---------- Performance bands (BE/AE/ME/EE) ----------
@bp.get("/performance-bands")
@require_auth
def list_bands():
    bands = scoped(PerformanceBand).order_by(PerformanceBand.min_score).all()
    return jsonify([b.to_dict() for b in bands])


@bp.post("/performance-bands")
@require_role(ADMIN)
def create_band():
    data = request.get_json(force=True) or {}
    required = ["code", "label", "min_score", "max_score"]
    if any(f not in data for f in required):
        return jsonify({"error": f"{required} are required"}), 400
    band = PerformanceBand(
        school_id=g.school_id,
        code=data["code"],
        label=data["label"],
        min_score=data["min_score"],
        max_score=data["max_score"],
        color=data.get("color"),
    )
    db.session.add(band)
    log_action(g.school_id, g.current_user.id, "PERFORMANCE_BAND_CREATED", "performance_band", band.id)
    db.session.commit()
    return jsonify(band.to_dict()), 201


def resolve_band(bands, score):
    if score is None:
        return None
    for b in bands:
        if b.min_score <= score <= b.max_score:
            return b
    return None
