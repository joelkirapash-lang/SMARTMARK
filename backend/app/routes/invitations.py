from datetime import datetime, timedelta, timezone

from flask import Blueprint, current_app, g, jsonify, request
from flask_jwt_extended import create_access_token, create_refresh_token

from app.extensions import db
from app.models import Invitation, InvitationStatus, DeliveryStatus, User, Role, UserStatus, School
from app.utils.auth import require_role, scoped
from app.utils.identity import generate_smartmark_email
from app.utils.security import generate_secure_token, hash_token, hash_password, validate_password_strength
from app.utils.mailer import send_invitation_email
from app.utils.audit import log_action

bp = Blueprint("invitations", __name__, url_prefix="/api")

TEACHER_ROLES = {Role.TEACHER.value, Role.EDUCATOR.value}
INVITABLE_ROLES = TEACHER_ROLES | {Role.STUDENT.value}


def _build_accept_url(raw_token: str) -> str:
    base = current_app.config["FRONTEND_BASE_URL"].rstrip("/")
    return f"{base}/accept-invitation/{raw_token}"


def _create_and_send_invitation(school: School, admin: User, role: str, payload: dict):
    if role not in INVITABLE_ROLES:
        raise ValueError("Invalid role for invitation")

    personal_email = (payload.get("personal_email") or "").strip().lower()
    first_name = (payload.get("first_name") or "").strip()
    second_name = (payload.get("second_name") or "").strip()
    other_name = (payload.get("other_name") or "").strip()

    if not personal_email or not first_name:
        raise ValueError("first_name and personal_email are required")

    smartmark_email = generate_smartmark_email(school.slug, first_name, second_name, role)

    user = User(
        school_id=school.id,
        role=Role(role),
        first_name=first_name,
        second_name=second_name,
        other_name=other_name,
        gender=payload.get("gender"),
        personal_email=personal_email,
        phone_number=payload.get("phone_number"),
        smartmark_email=smartmark_email,
        status=UserStatus.INVITED,
    )

    if role in TEACHER_ROLES:
        user.employee_id = payload.get("employee_id")
        user.home_grade_id = payload.get("home_grade_id")
        user.home_stream_id = payload.get("home_stream_id")
    else:  # STUDENT
        user.admission_number = payload.get("admission_number")
        dob = payload.get("date_of_birth")
        if dob:
            user.date_of_birth = datetime.strptime(dob, "%Y-%m-%d").date()
        user.grade_id = payload.get("grade_id")
        user.stream_id = payload.get("stream_id")
        user.guardian_name = payload.get("guardian_name")
        user.guardian_phone = payload.get("guardian_phone")
        user.guardian_email = payload.get("guardian_email")

    db.session.add(user)
    db.session.flush()

    raw_token = generate_secure_token()
    ttl_hours = school.invitation_ttl_hours or current_app.config["INVITATION_TOKEN_TTL_HOURS"]

    invitation = Invitation(
        school_id=school.id,
        invited_by_user_id=admin.id,
        user_id=user.id,
        recipient_name=user.full_name(),
        personal_email=personal_email,
        smartmark_email=smartmark_email,
        role=role,
        token_hash=hash_token(raw_token),
        status=InvitationStatus.PENDING,
        expires_at=datetime.now(timezone.utc) + timedelta(hours=ttl_hours),
    )
    db.session.add(invitation)
    db.session.flush()

    accept_url = _build_accept_url(raw_token)
    delivered = send_invitation_email(
        to_email=personal_email,
        recipient_name=invitation.recipient_name,
        role=role,
        school_name=school.name,
        smartmark_email=smartmark_email,
        accept_url=accept_url,
        expires_in_hours=ttl_hours,
    )

    now = datetime.now(timezone.utc)
    if delivered:
        invitation.status = InvitationStatus.SENT
        invitation.delivery_status = DeliveryStatus.SENT
        invitation.sent_at = now
        invitation.last_sent_at = now
        log_action(school.id, admin.id, "INVITATION_SENT", "invitation", invitation.id, {"personal_email": personal_email})
    else:
        invitation.delivery_status = DeliveryStatus.FAILED
        log_action(school.id, admin.id, "INVITATION_EMAIL_FAILED", "invitation", invitation.id)

    db.session.commit()
    return invitation, user


@bp.post("/invitations")
@require_role(Role.SCHOOL_ADMIN.value)
def create_invitation():
    data = request.get_json(force=True) or {}
    role = data.get("role")
    school = School.query.get(g.school_id)
    try:
        invitation, user = _create_and_send_invitation(school, g.current_user, role, data)
    except ValueError as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400
    return jsonify({"invitation": invitation.to_dict(), "user": user.to_dict()}), 201


@bp.get("/invitations")
@require_role(Role.SCHOOL_ADMIN.value)
def list_invitations():
    invitations = scoped(Invitation).order_by(Invitation.created_at.desc()).all()
    return jsonify([i.to_dict() for i in invitations])


@bp.post("/invitations/<invitation_id>/resend")
@require_role(Role.SCHOOL_ADMIN.value)
def resend_invitation(invitation_id):
    invitation = scoped(Invitation).filter_by(id=invitation_id).first()
    if invitation is None:
        return jsonify({"error": "Not found"}), 404
    if invitation.status == InvitationStatus.ACCEPTED:
        return jsonify({"error": "Invitation already accepted"}), 400

    school = School.query.get(g.school_id)
    raw_token = generate_secure_token()
    ttl_hours = school.invitation_ttl_hours or current_app.config["INVITATION_TOKEN_TTL_HOURS"]

    invitation.token_hash = hash_token(raw_token)  # old token invalidated implicitly
    invitation.expires_at = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
    invitation.status = InvitationStatus.PENDING
    invitation.cancelled_at = None

    accept_url = _build_accept_url(raw_token)
    delivered = send_invitation_email(
        to_email=invitation.personal_email,
        recipient_name=invitation.recipient_name,
        role=invitation.role,
        school_name=school.name,
        smartmark_email=invitation.smartmark_email,
        accept_url=accept_url,
        expires_in_hours=ttl_hours,
    )

    now = datetime.now(timezone.utc)
    if delivered:
        invitation.status = InvitationStatus.SENT
        invitation.delivery_status = DeliveryStatus.SENT
        invitation.last_sent_at = now
    else:
        invitation.delivery_status = DeliveryStatus.FAILED

    log_action(g.school_id, g.current_user.id, "INVITATION_RESENT", "invitation", invitation.id)
    db.session.commit()
    return jsonify({"invitation": invitation.to_dict()})


@bp.post("/invitations/<invitation_id>/cancel")
@require_role(Role.SCHOOL_ADMIN.value)
def cancel_invitation(invitation_id):
    invitation = scoped(Invitation).filter_by(id=invitation_id).first()
    if invitation is None:
        return jsonify({"error": "Not found"}), 404
    invitation.status = InvitationStatus.CANCELLED
    invitation.cancelled_at = datetime.now(timezone.utc)
    log_action(g.school_id, g.current_user.id, "INVITATION_CANCELLED", "invitation", invitation.id)
    db.session.commit()
    return jsonify({"invitation": invitation.to_dict()})


def _find_invitation_by_raw_token(raw_token: str):
    return Invitation.query.filter_by(token_hash=hash_token(raw_token)).first()


@bp.get("/invitations/verify/<raw_token>")
def verify_invitation(raw_token):
    """Public - validates a token without exposing any info about tokens
    that don't match (no user/school enumeration)."""
    invitation = _find_invitation_by_raw_token(raw_token)
    generic_invalid = {"valid": False, "reason": "invalid"}, 200

    if invitation is None:
        return generic_invalid

    if invitation.status == InvitationStatus.CANCELLED:
        return {"valid": False, "reason": "cancelled"}, 200
    if invitation.status == InvitationStatus.ACCEPTED:
        return {"valid": False, "reason": "already_used"}, 200
    if invitation.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        if invitation.status != InvitationStatus.EXPIRED:
            invitation.status = InvitationStatus.EXPIRED
            db.session.commit()
        return {"valid": False, "reason": "expired"}, 200

    school = School.query.get(invitation.school_id)
    return jsonify({
        "valid": True,
        "recipient_name": invitation.recipient_name,
        "role": invitation.role,
        "smartmark_email": invitation.smartmark_email,
        "school_name": school.name if school else None,
    })


@bp.post("/invitations/accept")
def accept_invitation():
    """Public - accepts the invitation and immediately requires the
    recipient to set their own password. The role/school/identity all come
    from the server-side invitation record, never from the request body."""
    data = request.get_json(force=True) or {}
    raw_token = data.get("token")
    password = data.get("password") or ""
    confirm_password = data.get("confirm_password") or ""

    if not raw_token:
        return jsonify({"error": "Missing token"}), 400
    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    pw_errors = validate_password_strength(password)
    if pw_errors:
        return jsonify({"error": "Weak password", "details": pw_errors}), 400

    invitation = _find_invitation_by_raw_token(raw_token)
    if invitation is None:
        return jsonify({"error": "This invitation link is invalid or no longer available."}), 400
    if invitation.status == InvitationStatus.CANCELLED:
        return jsonify({"error": "This invitation is no longer valid."}), 400
    if invitation.status == InvitationStatus.ACCEPTED:
        return jsonify({"error": "This invitation has already been used."}), 400
    if invitation.expires_at.replace(tzinfo=timezone.utc) < datetime.now(timezone.utc):
        invitation.status = InvitationStatus.EXPIRED
        db.session.commit()
        return jsonify({"error": "This invitation has expired."}), 400

    user = User.query.get(invitation.user_id)
    if user is None:
        return jsonify({"error": "This invitation link is invalid or no longer available."}), 400

    user.password_hash = hash_password(password)
    user.must_change_password = False
    user.status = UserStatus.ACTIVE
    user.activated_at = datetime.now(timezone.utc)

    invitation.status = InvitationStatus.ACCEPTED
    invitation.accepted_at = datetime.now(timezone.utc)

    log_action(user.school_id, user.id, "INVITATION_ACCEPTED", "invitation", invitation.id)
    log_action(user.school_id, user.id, "ACCOUNT_ACTIVATED", "user", user.id)
    db.session.commit()

    token = create_access_token(identity=user.id, additional_claims={"school_id": user.school_id, "role": user.role.value})
    refresh = create_refresh_token(identity=user.id, additional_claims={"school_id": user.school_id, "role": user.role.value})

    return jsonify({
        "user": user.to_dict(),
        "access_token": token,
        "refresh_token": refresh,
    })
