import os
from datetime import timedelta


class Config:
    """
    All configuration comes from environment variables.
    Nothing school-specific, no secrets, no defaults suitable for production
    are hardcoded here.
    """

    SECRET_KEY = os.environ.get("SECRET_KEY", "dev-secret-change-me")
    JWT_SECRET_KEY = os.environ.get("JWT_SECRET_KEY", "dev-jwt-secret-change-me")

    SQLALCHEMY_DATABASE_URI = os.environ.get(
        "DATABASE_URL", "sqlite:///smartmark_dev.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=8)
    JWT_REFRESH_TOKEN_EXPIRES = timedelta(days=14)

    INVITATION_TOKEN_TTL_HOURS = int(os.environ.get("INVITATION_TOKEN_TTL_HOURS", 48))

    # Public base URL of the frontend, used to build invitation links.
    # e.g. https://app.example.com  -> https://app.example.com/accept-invitation/<token>
    FRONTEND_BASE_URL = os.environ.get("FRONTEND_BASE_URL", "http://localhost:5173")

    # Email sending is pluggable. In dev, the console backend just logs the
    # email instead of sending it, so the workflow can be tested without a
    # real mail provider configured.
    MAIL_BACKEND = os.environ.get("MAIL_BACKEND", "console")  # console | smtp
    MAIL_FROM = os.environ.get("MAIL_FROM", "no-reply@example.com")
    SMTP_HOST = os.environ.get("SMTP_HOST")
    SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
    SMTP_USER = os.environ.get("SMTP_USER")
    SMTP_PASSWORD = os.environ.get("SMTP_PASSWORD")

    # File storage for crests/logos/photos is pluggable too; local disk in
    # dev, swap for S3/Cloudinary in production via STORAGE_BACKEND.
    STORAGE_BACKEND = os.environ.get("STORAGE_BACKEND", "local")
    LOCAL_STORAGE_DIR = os.environ.get("LOCAL_STORAGE_DIR", "uploads")


class TestConfig(Config):
    SQLALCHEMY_DATABASE_URI = "sqlite:///:memory:"
    TESTING = True
