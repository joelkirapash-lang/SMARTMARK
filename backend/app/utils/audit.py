from app.extensions import db
from app.models import AuditLog


def log_action(school_id, actor_user_id, action, target_type=None, target_id=None, meta=None):
    entry = AuditLog(
        school_id=school_id,
        actor_user_id=actor_user_id,
        action=action,
        target_type=target_type,
        target_id=target_id,
        meta=meta or {},
    )
    db.session.add(entry)
    # caller is responsible for committing as part of its own transaction
    return entry
