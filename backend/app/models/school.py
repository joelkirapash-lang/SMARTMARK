from app.extensions import db
from .base import gen_uuid, TimestampMixin


class School(db.Model, TimestampMixin):
    """
    The tenant. Created via the public registration flow. Everything else
    (name, crest, motto, colors, address, term dates, report footer) is
    configured by the school's own admin after signup - nothing about a
    specific school is ever hardcoded in application code.
    """

    __tablename__ = "schools"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)

    # Unique short slug used to build the school's SmartMark login domain,
    # e.g. "greenfield" -> firstname.lastname@teacher.greenfield.smartmark
    slug = db.Column(db.String(80), unique=True, nullable=False, index=True)

    name = db.Column(db.String(255), nullable=False)
    motto = db.Column(db.String(255))
    crest_url = db.Column(db.String(500))
    logo_url = db.Column(db.String(500))
    address = db.Column(db.String(255))
    contact_email = db.Column(db.String(255))
    contact_phone = db.Column(db.String(50))

    # Free-form branding the admin sets (colors etc.) - stored as JSON so
    # the schema never has to change per school.
    branding = db.Column(db.JSON, default=dict)

    current_term = db.Column(db.String(50))
    term_start = db.Column(db.Date)
    term_end = db.Column(db.Date)

    report_card_footer = db.Column(db.Text)

    invitation_ttl_hours = db.Column(db.Integer, default=48)

    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        return {
            "id": self.id,
            "slug": self.slug,
            "name": self.name,
            "motto": self.motto,
            "crest_url": self.crest_url,
            "logo_url": self.logo_url,
            "address": self.address,
            "contact_email": self.contact_email,
            "contact_phone": self.contact_phone,
            "branding": self.branding or {},
            "current_term": self.current_term,
            "term_start": self.term_start.isoformat() if self.term_start else None,
            "term_end": self.term_end.isoformat() if self.term_end else None,
            "report_card_footer": self.report_card_footer,
            "invitation_ttl_hours": self.invitation_ttl_hours,
        }
