from app.extensions import db
from .base import gen_uuid, TimestampMixin


class AuditLog(db.Model, TimestampMixin):
    __tablename__ = "audit_logs"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    school_id = db.Column(db.String(36), db.ForeignKey("schools.id"), nullable=False, index=True)
    actor_user_id = db.Column(db.String(36), db.ForeignKey("users.id"))
    action = db.Column(db.String(100), nullable=False)
    target_type = db.Column(db.String(50))
    target_id = db.Column(db.String(36))
    meta = db.Column(db.JSON, default=dict)

    def to_dict(self):
        return {
            "id": self.id,
            "actor_user_id": self.actor_user_id,
            "action": self.action,
            "target_type": self.target_type,
            "target_id": self.target_id,
            "meta": self.meta or {},
            "created_at": self.created_at.isoformat() if self.created_at else None,
        }


class ReportShareLink(db.Model, TimestampMixin):
    """A token-based, no-login link a parent can use to view one student's
    report card for one exam."""

    __tablename__ = "report_share_links"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    school_id = db.Column(db.String(36), db.ForeignKey("schools.id"), nullable=False, index=True)
    student_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    exam_id = db.Column(db.String(36), db.ForeignKey("exams.id"), nullable=False)
    token_hash = db.Column(db.String(128), nullable=False, index=True)
    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    revoked = db.Column(db.Boolean, default=False)
