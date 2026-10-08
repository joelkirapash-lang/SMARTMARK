import hashlib
import secrets

import bcrypt


def hash_password(plain_password: str) -> str:
    return bcrypt.hashpw(plain_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")


def verify_password(plain_password: str, password_hash: str) -> bool:
    if not password_hash:
        return False
    return bcrypt.checkpw(plain_password.encode("utf-8"), password_hash.encode("utf-8"))


def generate_secure_token() -> str:
    """Cryptographically random token. Never derived from any user data
    (name, admission number, DOB, phone, school name, etc.)."""
    return secrets.token_urlsafe(32)


def hash_token(raw_token: str) -> str:
    """Only this hash is ever stored - the raw token exists only in the
    outgoing invitation URL and the recipient's browser."""
    return hashlib.sha256(raw_token.encode("utf-8")).hexdigest()


PASSWORD_MIN_LENGTH = 8


def validate_password_strength(password: str) -> list[str]:
    errors = []
    if not password or len(password) < PASSWORD_MIN_LENGTH:
        errors.append(f"Password must be at least {PASSWORD_MIN_LENGTH} characters.")
    if not any(c.isupper() for c in password or ""):
        errors.append("Password must contain an uppercase letter.")
    if not any(c.islower() for c in password or ""):
        errors.append("Password must contain a lowercase letter.")
    if not any(c.isdigit() for c in password or ""):
        errors.append("Password must contain a number.")
    return errors
