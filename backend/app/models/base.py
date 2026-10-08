import uuid
from datetime import datetime, timezone

from app.extensions import db


def gen_uuid():
    return str(uuid.uuid4())


def utcnow():
    return datetime.now(timezone.utc)


class TimestampMixin:
    created_at = db.Column(db.DateTime(timezone=True), default=utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime(timezone=True), default=utcnow, onupdate=utcnow, nullable=False
    )


class TenantMixin:
    """
    Every table holding school-specific data mixes this in. school_id is
    always required and every query must filter by it - see
    app/utils/tenant.py for the enforced query helper.
    """

    @staticmethod
    def _school_fk():
        return db.Column(
            db.String(36), db.ForeignKey("schools.id"), nullable=False, index=True
        )
