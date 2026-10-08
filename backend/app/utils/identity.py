import re
import unicodedata

from app.models import User


def _normalize_name_part(value: str) -> str:
    if not value:
        return ""
    # Normalize unicode accents to closest ASCII equivalent.
    value = unicodedata.normalize("NFKD", value).encode("ascii", "ignore").decode("ascii")
    value = value.lower().strip()
    value = value.replace("'", "")
    value = re.sub(r"[\s_-]+", ".", value)  # spaces/hyphens/underscores -> dot
    value = re.sub(r"[^a-z0-9.]", "", value)  # strip any other unsupported chars
    value = re.sub(r"\.+", ".", value).strip(".")
    return value


def _role_segment(role: str) -> str:
    return {
        "TEACHER": "teacher",
        "EDUCATOR": "educator",
        "STUDENT": "student",
        "SCHOOL_ADMIN": "admin",
    }.get(role, role.lower())


def generate_smartmark_email(school_slug: str, first_name: str, second_name: str, role: str) -> str:
    """
    Builds firstname.secondname@role.<school-slug>.smartmark, normalized,
    and guarantees uniqueness within the school by appending a numeric
    suffix deterministically if a collision exists. Never overwrites an
    existing account.
    """
    base = ".".join(
        p for p in [_normalize_name_part(first_name), _normalize_name_part(second_name)] if p
    )
    if not base:
        base = "user"

    domain = f"{_role_segment(role)}.{school_slug}.smartmark"

    candidate = f"{base}@{domain}"
    suffix = 1
    while User.query.filter_by(smartmark_email=candidate).first() is not None:
        suffix += 1
        candidate = f"{base}{suffix}@{domain}"
    return candidate
