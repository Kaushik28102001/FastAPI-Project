import resend
from fastapi.templating import Jinja2Templates

from config import settings

templates = Jinja2Templates(directory="templates")

resend.api_key = settings.resend_api_key.get_secret_value()


async def send_email(
    to_email: str,
    subject: str,
    plain_text: str,
    html_content: str | None = None,
) -> None:
    params: dict = {
        "from": settings.mail_from,
        "to": [to_email],
        "subject": subject,
        "text": plain_text,
    }

    if html_content:
        params["html"] = html_content

    resend.Emails.send(params)


async def send_otp_email(to_email: str, username: str, otp: str) -> None:
    subject = "Email Verification OTP - FastAPI Blog"

    plain_text = f"""Hi {username},

Welcome to FastAPI Blog!

Thank you for registering. Use the OTP below to verify your email address:

OTP: {otp}

This OTP will expire in 5 minutes.

If you did not create an account on FastAPI Blog, please ignore this email.

Best regards,
The FastAPI Blog Team
"""

    html_content = f"""
<!DOCTYPE html>
<html>
<head><meta charset="UTF-8"><title>Email Verification</title></head>
<body>
    <h2>Welcome to FastAPI Blog!</h2>
    <p>Hi <strong>{username}</strong>,</p>
    <p>Thank you for registering. Use the OTP below to verify your email address:</p>
    <h1>{otp}</h1>
    <p>This OTP will expire in <strong>5 minutes</strong>.</p>
    <p>If you did not create an account on FastAPI Blog, please ignore this email.</p>
    <br>
    <p>Best regards,<br><strong>The FastAPI Blog Team</strong></p>
</body>
</html>
"""

    await send_email(
        to_email=to_email,
        subject=subject,
        plain_text=plain_text,
        html_content=html_content,
    )


async def send_password_reset_email(to_email: str, username: str, token: str) -> None:
    reset_url = f"{settings.frontend_url}/reset-password?token={token}"

    template = templates.env.get_template("email/password_reset.html")
    html_content = template.render(reset_url=reset_url, username=username)

    plain_text = f"""Hi {username},

You requested to reset your password. Click the link below to set a new password:

{reset_url}

This link will expire in 1 hour.

If you didn't request this, you can safely ignore this email.

Best regards,
The FastAPI Blog Team
"""

    await send_email(
        to_email=to_email,
        subject="Reset Your Password - FastAPI Blog",
        plain_text=plain_text,
        html_content=html_content,
    )