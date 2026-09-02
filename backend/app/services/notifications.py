import json
import os
import secrets
from datetime import datetime, timedelta
from email.utils import formataddr
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

from dotenv import load_dotenv
from sqlalchemy.orm import Session

from app.models.user import User

load_dotenv()


def generate_numeric_code(length: int = 6) -> str:
    return "".join(secrets.choice("0123456789") for _ in range(length))


def _send_email(destination: str, subject: str, body: str) -> None:
    """Send email using the Resend API.

    Required Railway variables:
    RESEND_API_KEY=your_resend_api_key
    FROM_EMAIL=noreply@freesd.org
    """

    resend_api_key = os.getenv("RESEND_API_KEY")
    from_email = os.getenv("FROM_EMAIL", "noreply@freesd.org")

    if not resend_api_key:
        print("\n" + "=" * 50)
        print(f"LOCAL DEVELOPMENT EMAIL TO: {destination}")
        print(f"SUBJECT: {subject}")
        print(body)
        print("=" * 50 + "\n")
        return

    payload = {
        "from": formataddr(("Free SD", from_email)),
        "to": [destination],
        "subject": subject,
        "text": body,
    }

    request = Request(
        "https://api.resend.com/emails",
        data=json.dumps(payload).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {resend_api_key}",
            "Content-Type": "application/json",
            "User-Agent": "freesd-backend/1.0",
        },
        method="POST",
    )

    try:
        with urlopen(request, timeout=30) as response:
            response_body = response.read().decode("utf-8")
            if response.status >= 400:
                raise RuntimeError(f"Resend email failed: {response.status} {response_body}")
    except HTTPError as e:
        error_body = e.read().decode("utf-8")
        raise RuntimeError(f"Resend email failed: {e.code} {error_body}") from e
    except URLError as e:
        raise RuntimeError(f"Could not connect to Resend: {e}") from e

    print(f"[Free SD EMAIL] Sent email to {destination}")


def send_code(destination: str, code: str, delivery_method: str) -> None:
    """Send an OTP verification code to the user logging in."""

    if delivery_method != "email":
        raise RuntimeError("Only email verification is currently supported.")

    subject = "Your Free SD verification code"
    body = f"Your Free SD verification code is: {code}\n\nThis code expires in 10 minutes."

    _send_email(destination, subject, body)


def send_reset_message(destination: str, token: str, delivery_method: str) -> None:
    """Send a password reset link to the user."""

    if delivery_method != "email":
        raise RuntimeError("Only email password reset is currently supported.")

    frontend_url = os.getenv("FRONTEND_URL", "http://localhost:5173")
    reset_url = f"{frontend_url.rstrip('/')}/reset-password?token={token}"

    subject = "Reset your Free SD password"
    body = (
        "Use this link to reset your Free SD password:\n\n"
        f"{reset_url}\n\n"
        "This link expires in 30 minutes."
    )

    _send_email(destination, subject, body)


def create_and_send_otp(db: Session, user: User, delivery_method: str) -> None:
    code = generate_numeric_code()
    user.pending_otp = code
    user.pending_otp_expires_at = datetime.utcnow() + timedelta(minutes=10)
    db.add(user)
    db.commit()

    destination = user.email if delivery_method == "email" else (user.phone or user.email)
    send_code(destination, code, delivery_method)


def create_and_send_reset(db: Session, user: User, delivery_method: str) -> None:
    token = secrets.token_urlsafe(32)
    user.reset_token = token
    user.reset_token_expires_at = datetime.utcnow() + timedelta(minutes=30)
    db.add(user)
    db.commit()

    destination = user.email if delivery_method == "email" else (user.phone or user.email)
    send_reset_message(destination, token, delivery_method)
