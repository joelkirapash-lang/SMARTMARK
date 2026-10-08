from flask import Blueprint, g, jsonify, request

from app.models import User, Exam, Mark, Subject, PerformanceBand, Role, Grade
from app.utils.auth import require_auth, scoped
from app.routes.academics import resolve_band

bp = Blueprint("dashboard", __name__, url_prefix="/api")


@bp.get("/dashboard/summary")
@require_auth
def dashboard_summary():
    exam_id = request.args.get("exam_id")
    prior_exam_id = request.args.get("prior_exam_id")

    student_count = scoped(User).filter_by(role=Role.STUDENT, is_archived=False).count()
    teacher_count = scoped(User).filter(User.role.in_([Role.TEACHER, Role.EDUCATOR])).count()
    grade_count = scoped(Grade).filter_by(is_archived=False).count()

    data = {
        "student_count": student_count,
        "teacher_count": teacher_count,
        "grade_count": grade_count,
    }

    if exam_id:
        marks = scoped(Mark).filter_by(exam_id=exam_id).all()
        subjects = {s.id: s for s in scoped(Subject).all()}
        bands = scoped(PerformanceBand).order_by(PerformanceBand.min_score).all()

        subject_totals = {}
        for m in marks:
            if m.score is None:
                continue
            subject_totals.setdefault(m.subject_id, []).append(m.score)

        data["subject_averages"] = [
            {
                "subject": subjects[sid].name if sid in subjects else "Unknown",
                "average": round(sum(scores) / len(scores), 2),
            }
            for sid, scores in subject_totals.items()
        ]

        band_counts = {}
        for m in marks:
            band = resolve_band(bands, m.score)
            key = band.code if band else "Unranked"
            band_counts[key] = band_counts.get(key, 0) + 1
        data["performance_distribution"] = [{"band": k, "count": v} for k, v in band_counts.items()]

        if prior_exam_id:
            prior_marks = scoped(Mark).filter_by(exam_id=prior_exam_id).all()
            prior_by_student = {}
            for m in prior_marks:
                if m.score is not None:
                    prior_by_student.setdefault(m.student_id, []).append(m.score)
            current_by_student = {}
            for m in marks:
                if m.score is not None:
                    current_by_student.setdefault(m.student_id, []).append(m.score)

            improvements = []
            for sid, scores in current_by_student.items():
                if sid in prior_by_student:
                    cur_avg = sum(scores) / len(scores)
                    prior_avg = sum(prior_by_student[sid]) / len(prior_by_student[sid])
                    improvements.append({"student_id": sid, "delta": round(cur_avg - prior_avg, 2)})
            improvements.sort(key=lambda r: -r["delta"])

            students = {s.id: s for s in scoped(User).filter_by(role=Role.STUDENT).all()}
            for row in improvements[:10]:
                s = students.get(row["student_id"])
                row["student_name"] = s.full_name() if s else "Unknown"
            data["most_improved"] = improvements[:10]

    return jsonify(data)
