import enum

from app.extensions import db
from .base import gen_uuid, TimestampMixin


class Role(str, enum.Enum):
    SCHOOL_ADMIN = "SCHOOL_ADMIN"
    TEACHER = "TEACHER"
    EDUCATOR = "EDUCATOR"
    STUDENT = "STUDENT"


class UserStatus(str, enum.Enum):
    INVITED = "INVITED"
    ACTIVE = "ACTIVE"
    DISABLED = "DISABLED"


class User(db.Model, TimestampMixin):
    __tablename__ = "users"
    __table_args__ = (
        db.UniqueConstraint("school_id", "smartmark_email", name="uq_user_smartmark_email"),
    )

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    school_id = db.Column(db.String(36), db.ForeignKey("schools.id"), nullable=False, index=True)

    role = db.Column(db.Enum(Role), nullable=False)

    first_name = db.Column(db.String(100), nullable=False)
    second_name = db.Column(db.String(100))
    other_name = db.Column(db.String(100))
    gender = db.Column(db.String(20))

    # Existing external mailbox - used ONLY for invitation delivery / contact.
    personal_email = db.Column(db.String(255))
    phone_number = db.Column(db.String(50))

    # Generated SmartMark application login identity - this is what the
    # user actually authenticates with. Distinct from personal_email.
    smartmark_email = db.Column(db.String(255), nullable=False, index=True)

    password_hash = db.Column(db.String(255))
    must_change_password = db.Column(db.Boolean, default=False)

    status = db.Column(db.Enum(UserStatus), default=UserStatus.INVITED, nullable=False)
    activated_at = db.Column(db.DateTime(timezone=True))
    last_login_at = db.Column(db.DateTime(timezone=True))

    # --- Teacher / educator specific fields ---
    employee_id = db.Column(db.String(50))
    home_grade_id = db.Column(db.String(36), db.ForeignKey("grades.id"))
    home_stream_id = db.Column(db.String(36), db.ForeignKey("streams.id"))

    # --- Student specific fields ---
    admission_number = db.Column(db.String(50), index=True)
    date_of_birth = db.Column(db.Date)
    grade_id = db.Column(db.String(36), db.ForeignKey("grades.id"))
    stream_id = db.Column(db.String(36), db.ForeignKey("streams.id"))
    guardian_name = db.Column(db.String(200))
    guardian_phone = db.Column(db.String(50))
    guardian_email = db.Column(db.String(255))
    photo_url = db.Column(db.String(500))
    is_archived = db.Column(db.Boolean, default=False)  # set on year-end promotion/graduation

    def full_name(self):
        parts = [self.first_name, self.second_name, self.other_name]
        return " ".join(p for p in parts if p)

    def to_dict(self, include_sensitive=False):
        data = {
            "id": self.id,
            "school_id": self.school_id,
            "role": self.role.value if self.role else None,
            "first_name": self.first_name,
            "second_name": self.second_name,
            "other_name": self.other_name,
            "gender": self.gender,
            "personal_email": self.personal_email,
            "phone_number": self.phone_number,
            "smartmark_email": self.smartmark_email,
            "status": self.status.value if self.status else None,
            "employee_id": self.employee_id,
            "home_grade_id": self.home_grade_id,
            "home_stream_id": self.home_stream_id,
            "admission_number": self.admission_number,
            "date_of_birth": self.date_of_birth.isoformat() if self.date_of_birth else None,
            "grade_id": self.grade_id,
            "stream_id": self.stream_id,
            "guardian_name": self.guardian_name,
            "guardian_phone": self.guardian_phone,
            "guardian_email": self.guardian_email,
            "photo_url": self.photo_url,
        }
        return data
