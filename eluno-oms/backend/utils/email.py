"""SMTP email utilities for operational alerts."""

import logging
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText

from backend.config import settings

logger = logging.getLogger(__name__)


def send_alert_email(subject: str, body: str) -> bool:
    """Send an alert email via SMTP. Returns True on success."""
    if not settings.smtp_user or not settings.smtp_password:
        logger.warning("SMTP credentials not configured; skipping email send.")
        return False

    try:
        msg = MIMEMultipart()
        msg["From"] = settings.alert_from_email
        msg["To"] = settings.alert_to_email
        msg["Subject"] = subject
        msg.attach(MIMEText(body, "plain"))

        with smtplib.SMTP(settings.smtp_host, settings.smtp_port) as server:
            server.starttls()
            server.login(settings.smtp_user, settings.smtp_password)
            server.send_message(msg)
        return True
    except Exception as exc:
        logger.error("Failed to send alert email: %s", exc)
        return False
