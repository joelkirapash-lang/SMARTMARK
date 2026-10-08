from app.extensions import db
from .base import gen_uuid, TimestampMixin


class Grade(db.Model, TimestampMixin):
    """A CBC level: Playgroup, PP1, PP2, Grade 1 .. Grade 10. Created by the
    admin - nothing is pre-seeded."""

    __tablename__ = "grades"
    __table_args__ = (db.UniqueConstraint("school_id", "name", name="uq_grade_name"),)

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    school_id = db.Column(db.String(36), db.ForeignKey("schools.id"), nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)
    order_index = db.Column(db.Integer, default=0)  # for sorting Playgroup -> Grade 10
    is_archived = db.Column(db.Boolean, default=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "order_index": self.order_index}


class Stream(db.Model, TimestampMixin):
    __tablename__ = "streams"
    __table_args__ = (db.UniqueConstraint("grade_id", "name", name="uq_stream_name"),)

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    school_id = db.Column(db.String(36), db.ForeignKey("schools.id"), nullable=False, index=True)
    grade_id = db.Column(db.String(36), db.ForeignKey("grades.id"), nullable=False, index=True)
    name = db.Column(db.String(50), nullable=False)

    def to_dict(self):
        return {"id": self.id, "grade_id": self.grade_id, "name": self.name}


class Subject(db.Model, TimestampMixin):
    __tablename__ = "subjects"
    __table_args__ = (db.UniqueConstraint("school_id", "code", name="uq_subject_code"),)

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    school_id = db.Column(db.String(36), db.ForeignKey("schools.id"), nullable=False, index=True)
    name = db.Column(db.String(100), nullable=False)
    code = db.Column(db.String(20), nullable=False)

    def to_dict(self):
        return {"id": self.id, "name": self.name, "code": self.code}


class GradeSubject(db.Model, TimestampMixin):
    """Which subjects are offered at which grade."""

    __tablename__ = "grade_subjects"
    __table_args__ = (db.UniqueConstraint("grade_id", "subject_id", name="uq_grade_subject"),)

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    school_id = db.Column(db.String(36), db.ForeignKey("schools.id"), nullable=False, index=True)
    grade_id = db.Column(db.String(36), db.ForeignKey("grades.id"), nullable=False, index=True)
    subject_id = db.Column(db.String(36), db.ForeignKey("subjects.id"), nullable=False, index=True)


class PerformanceBand(db.Model, TimestampMixin):
    """Configurable CBC score bands, e.g. BE 0-49, AE 50-64, ME 65-79, EE 80-100.
    Each school configures its own bands; nothing is hardcoded."""

    __tablename__ = "performance_bands"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    school_id = db.Column(db.String(36), db.ForeignKey("schools.id"), nullable=False, index=True)
    code = db.Column(db.String(10), nullable=False)  # BE / AE / ME / EE
    label = db.Column(db.String(100), nullable=False)  # e.g. "Exceeding Expectation"
    min_score = db.Column(db.Float, nullable=False)
    max_score = db.Column(db.Float, nullable=False)
    color = db.Column(db.String(20))

    def to_dict(self):
        return {
            "id": self.id,
            "code": self.code,
            "label": self.label,
            "min_score": self.min_score,
            "max_score": self.max_score,
            "color": self.color,
        }


class TeacherAssignment(db.Model, TimestampMixin):
    """Additional authorized grade/stream/subject combinations for a teacher,
    beyond their home grade/stream. Only an admin can create/modify these -
    teachers cannot self-assign."""

    __tablename__ = "teacher_assignments"

    id = db.Column(db.String(36), primary_key=True, default=gen_uuid)
    school_id = db.Column(db.String(36), db.ForeignKey("schools.id"), nullable=False, index=True)
    teacher_id = db.Column(db.String(36), db.ForeignKey("users.id"), nullable=False, index=True)
    grade_id = db.Column(db.String(36), db.ForeignKey("grades.id"), nullable=False)
    stream_id = db.Column(db.String(36), db.ForeignKey("streams.id"))
    subject_id = db.Column(db.String(36), db.ForeignKey("subjects.id"), nullable=False)

    def to_dict(self):
        return {
            "id": self.id,
            "teacher_id": self.teacher_id,
            "grade_id": self.grade_id,
            "stream_id": self.stream_id,
            "subject_id": self.subject_id,
        }
