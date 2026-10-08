import smtplib
from email.mime.text import MIMEText

from flask import current_app


def send_invitation_email(to_email: str, recipient_name: str, role: str, school_name: str,
                           smartmark_email: str, accept_url: str, expires_in_hours: int) -> bool:
    subject = f"You're invited to join {school_name} on SmartMark"
    body = (
        f"Hello {recipient_name},\n\n"
        f"You have been invited to join {school_name} on SmartMark as a {role.title()}.\n\n"
        f"Your SmartMark account: {smartmark_email}\n\n"
        f"Accept your invitation and set up your account here:\n{accept_url}\n\n"
        f"This invitation expires in {expires_in_hours} hours.\n\n"
        f"If you were not expecting this invitation, you can safely ignore this email.\n\n"
        f"Regards,\n{school_name}\nSmartMark"
    )

    backend = current_app.config.get("MAIL_BACKEND", "console")

    if backend == "console":
        current_app.logger.warning("---- INVITATION EMAIL (console backend) ----")
        current_app.logger.warning("To: %s\nSubject: %s\n\n%s", to_email, subject, body)
        current_app.logger.warning("---------------------------------------------")
        return True

    if backend == "smtp":
        try:
            msg = MIMEText(body)
            msg["Subject"] = subject
            msg["From"] = current_app.config["MAIL_FROM"]
            msg["To"] = to_email
            with smtplib.SMTP(current_app.config["SMTP_HOST"], current_app.config["SMTP_PORT"]) as server:
                server.starttls()
                if current_app.config.get("SMTP_USER"):
                    server.login(current_app.config["SMTP_USER"], current_app.config["SMTP_PASSWORD"])
                server.sendmail(current_app.config["MAIL_FROM"], [to_email], msg.as_string())
            return True
        except Exception:
            current_app.logger.exception("Failed to send invitation email via SMTP")
            return False

    current_app.logger.warning("Unknown MAIL_BACKEND '%s' - email not sent", backend)
    return False
