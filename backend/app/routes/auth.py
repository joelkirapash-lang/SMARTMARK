import re
from datetime import datetime, timezone

from flask import Blueprint, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token, jwt_required, get_jwt_identity

from app.extensions import db
from app.models import School, User, Role, UserStatus
from app.utils.identity import generate_smartmark_email
from app.utils.security import hash_password, verify_password, validate_password_strength
from app.utils.audit import log_action
from app.utils.auth import load_current_user

bp = Blueprint("auth", __name__, url_prefix="/api")

SLUG_RE = re.compile(r"^[a-z0-9-]{3,60}$")


def slugify(name: str) -> str:
    s = name.lower().strip()
    s = re.sub(r"[^a-z0-9]+", "-", s)
    return re.sub(r"-+", "-", s).strip("-")


@bp.post("/schools/register")
def register_school():
    """
    Public endpoint: a brand new school signs up. Creates the tenant (School)
    completely empty - no seed grades/streams/subjects/students - and its
    first user, who becomes SCHOOL_ADMIN for that tenant only.
    """
    data = request.get_json(force=True) or {}
    school_name = (data.get("school_name") or "").strip()
    admin_first_name = (data.get("first_name") or "").strip()
    admin_second_name = (data.get("second_name") or "").strip()
    admin_personal_email = (data.get("email") or "").strip().lower()
    password = data.get("password") or ""

    if not school_name or not admin_first_name or not admin_personal_email:
        return jsonify({"error": "school_name, first_name and email are required"}), 400

    pw_errors = validate_password_strength(password)
    if pw_errors:
        return jsonify({"error": "Weak password", "details": pw_errors}), 400

    base_slug = slugify(school_name) or "school"
    slug = base_slug
    n = 1
    while School.query.filter_by(slug=slug).first() is not None:
        n += 1
        slug = f"{base_slug}-{n}"

    school = School(slug=slug, name=school_name)
    db.session.add(school)
    db.session.flush()  # get school.id before generating the admin email

    smartmark_email = generate_smartmark_email(slug, admin_first_name, admin_second_name, Role.SCHOOL_ADMIN.value)

    admin = User(
        school_id=school.id,
        role=Role.SCHOOL_ADMIN,
        first_name=admin_first_name,
        second_name=admin_second_name,
        personal_email=admin_personal_email,
        smartmark_email=smartmark_email,
        password_hash=hash_password(password),
        status=UserStatus.ACTIVE,
        activated_at=datetime.now(timezone.utc),
    )
    db.session.add(admin)
    db.session.flush()

    log_action(school.id, admin.id, "SCHOOL_REGISTERED", "school", school.id)
    log_action(school.id, admin.id, "ADMIN_ACCOUNT_CREATED", "user", admin.id)
    db.session.commit()

    token = create_access_token(
        identity=admin.id, additional_claims={"school_id": school.id, "role": admin.role.value}
    )
    refresh = create_refresh_token(identity=admin.id, additional_claims={"school_id": school.id, "role": admin.role.value})

    return jsonify({
        "school": school.to_dict(),
        "user": admin.to_dict(),
        "smartmark_email": smartmark_email,
        "access_token": token,
        "refresh_token": refresh,
    }), 201


@bp.post("/auth/login")
def login():
    data = request.get_json(force=True) or {}
    identifier = (data.get("smartmark_email") or "").strip().lower()
    password = data.get("password") or ""

    if not identifier or not password:
        return jsonify({"error": "smartmark_email and password are required"}), 400

    user = User.query.filter_by(smartmark_email=identifier).first()
    if user is None or not verify_password(password, user.password_hash):
        # Generic message - never reveal whether the account exists.
        return jsonify({"error": "Invalid credentials"}), 401

    if user.status != UserStatus.ACTIVE:
        return jsonify({"error": "Account is not active yet. Check your invitation email."}), 403

    user.last_login_at = datetime.now(timezone.utc)
    db.session.commit()

    token = create_access_token(identity=user.id, additional_claims={"school_id": user.school_id, "role": user.role.value})
    refresh = create_refresh_token(identity=user.id, additional_claims={"school_id": user.school_id, "role": user.role.value})

    return jsonify({
        "user": user.to_dict(),
        "must_change_password": user.must_change_password,
        "access_token": token,
        "refresh_token": refresh,
    })


@bp.get("/auth/me")
@jwt_required()
def me():
    user = load_current_user()
    if user is None:
        return jsonify({"error": "Not found"}), 404
    school = School.query.get(user.school_id)
    return jsonify({"user": user.to_dict(), "school": school.to_dict() if school else None})


@bp.post("/auth/refresh")
@jwt_required(refresh=True)
def refresh():
    identity = get_jwt_identity()
    user = User.query.get(identity)
    if user is None:
        return jsonify({"error": "Not found"}), 404
    token = create_access_token(identity=user.id, additional_claims={"school_id": user.school_id, "role": user.role.value})
    return jsonify({"access_token": token})
