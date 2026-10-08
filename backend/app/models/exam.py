from app.extensions import db
from .base import gen_uuid, TimestampMixin


class Exam(db.Model, TimestampMixin):
    __tablename__ = "exams"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    school_id = db.Column(db.String(36), db.ForeignKey("schools.id"), nullable=False, index=True)
    name = db.Column(db.String(150), nullable=False)  # e.g. "Term 2 Mid-Term"
    term = db.Column(db.String(50))
    exam_date = db.Column(db.Date)
    is_published = db.Column(db.Boolean, default=False)  # report cards / parent links visible once published
    created_by_user_id = db.Column(db.String(36), db.ForeignKey("users.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "name": self.name,
            "term": self.term,
            "exam_date": self.exam_date.isoformat() if self.exam_date else None,
            "is_published": self.is_published,
        }


class Mark(db.Model, TimestampMixin):
    __tablename__ = "marks"
    __table_args__ = (
        db.UniqueConstraint("exam_id", "student_id", "subject_id", name="uq_mark_unique"),
    )

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    school_id = db.Column(db.String(36), db.ForeignKey("schools.id"), nullable=False, index=True)
    exam_id = db.Column(db.String(36), db.ForeignKey("exams.id"), nullable=False, index=True)
    student_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    subject_id = db.Column(db.String(36), db.ForeignKey("subjects.id"), nullable=False, index=True)
    grade_id = db.Column(db.String(36), db.ForeignKey("grades.id"), nullable=False)
    stream_id = db.Column(db.String(36), db.ForeignKey("streams.id"))

    score = db.Column(db.Float)
    max_score = db.Column(db.Float, default=100)
    remark = db.Column(db.Text)

    entered_by_user_id = db.Column(db.String(36), db.ForeignKey("users.id"))

    def to_dict(self):
        return {
            "id": self.id,
            "exam_id": self.exam_id,
            "student_id": self.student_id,
            "subject_id": self.subject_id,
            "score": self.score,
            "max_score": self.max_score,
            "remark": self.remark,
        }
