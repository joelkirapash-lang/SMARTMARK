from flask import Blueprint, g, jsonify, request

from app.extensions import db
from app.models import School, Role
from app.utils.auth import require_auth, require_role
from app.utils.audit import log_action

bp = Blueprint("school_settings", __name__, url_prefix="/api")


@bp.get("/school")
@require_auth
def get_school():
    school = School.query.get(g.school_id)
    return jsonify(school.to_dict())


@bp.put("/school")
@require_role(Role.SCHOOL_ADMIN.value)
def update_school():
    school = School.query.get(g.school_id)
    data = request.get_json(force=True) or {}
    for field in [
        "name", "motto", "crest_url", "logo_url", "address", "contact_email",
        "contact_phone", "current_term", "report_card_footer", "invitation_ttl_hours",
    ]:
        if field in data:
            setattr(school, field, data[field])
    if "branding" in data:
        school.branding = data["branding"]
    log_action(g.school_id, g.current_user.id, "SCHOOL_SETTINGS_UPDATED", "school", school.id)
    db.session.commit()
    return jsonify(school.to_dict())


@bp.get("/audit-log")
@require_role(Role.SCHOOL_ADMIN.value)
def get_audit_log():
    from app.models import AuditLog
    from app.utils.auth import scoped
    logs = scoped(AuditLog).order_by(AuditLog.created_at.desc()).limit(200).all()
    return jsonify([l.to_dict() for l in logs])
