import enum

from app.extensions import db
from .base import gen_uuid, TimestampMixin


class InvitationStatus(str, enum.Enum):
    PENDING = "PENDING"
    SENT = "SENT"
    ACCEPTED = "ACCEPTED"
    EXPIRED = "EXPIRED"
    CANCELLED = "CANCELLED"
    FAILED = "FAILED"


class DeliveryStatus(str, enum.Enum):
    NOT_SENT = "NOT_SENT"
    SENT = "SENT"
    FAILED = "FAILED"


class Invitation(db.Model, TimestampMixin):
    __tablename__ = "invitations"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    school_id = db.Column(db.String(36), db.ForeignKey("schools.id"), nullable=False, index=True)
    invited_by_user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)
    user_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False)

    recipient_name = db.Column(db.String(255), nullable=False)
    personal_email = db.Column(db.String(255), nullable=False)
    smartmark_email = db.Column(db.String(255), nullable=False)
    role = db.Column(db.String(20), nullable=False)

    # Only the hash is stored. The raw token exists only in the outgoing
    # email URL and is never persisted.
    token_hash = db.Column(db.String(128), nullable=False, index=True)

    status = db.Column(db.Enum(InvitationStatus), default=InvitationStatus.PENDING, nullable=False)
    delivery_status = db.Column(db.Enum(DeliveryStatus), default=DeliveryStatus.NOT_SENT)

    expires_at = db.Column(db.DateTime(timezone=True), nullable=False)
    sent_at = db.Column(db.DateTime(timezone=True))
    accepted_at = db.Column(db.DateTime(timezone=True))
    cancelled_at = db.Column(db.DateTime(timezone=True))
    last_sent_at = db.Column(db.DateTime(timezone=True))

    def to_dict(self):
        return {
            "id": self.id,
            "recipient_name": self.recipient_name,
            "personal_email": self.personal_email,
            "smartmark_email": self.smartmark_email,
            "role": self.role,
            "status": self.status.value if self.status else None,
            "delivery_status": self.delivery_status.value if self.delivery_status else None,
            "expires_at": self.expires_at.isoformat() if self.expires_at else None,
            "sent_at": self.sent_at.isoformat() if self.sent_at else None,
            "accepted_at": self.accepted_at.isoformat() if self.accepted_at else None,
            "cancelled_at": self.cancelled_at.isoformat() if self.cancelled_at else None,
        }
