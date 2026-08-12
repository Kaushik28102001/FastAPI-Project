from email.message import EmailMessage

import aiosmtplib
from fastapi.templating import Jinja2Templates

from config import settings

templates = Jinja2Templates(directory="templates")


async def send_email(
    to_email: str,
    subject: str,
    plain_text: str,
    html_content: str | None = None,
) -> None:

    message = EmailMessage()

    message["From"] = settings.mail_from
    message["To"] = to_email
    message["Subject"] = subject

    message.set_content(plain_text)

    if html_content:
        message.add_alternative(
            html_content,
            subtype="html",
        )

    await aiosmtplib.send(
        message,
        hostname=settings.mail_server,
        port=587,
        username=settings.mail_username,
        password=settings.mail_password,
        start_tls=True,
    )
async def send_otp_email(
            to_email: str,
            username: str,
            otp: str,
        ) -> None:

            subject = "Email Verification OTP - FastAPI Blog"

            plain_text = f"""
        Hi {username},

        Your verification OTP is:

        {otp}

        This OTP will expire in 10 minutes.

        If you did not create an account, please ignore this email.

        FastAPI Blog Team
        """

            html_content = f"""
            <h2>Email Verification</h2>

            <p>Hi {username},</p>

            <p>Your verification OTP is:</p>

            <h1>{otp}</h1>

            <p>This OTP will expire in 10 minutes.</p>

            <p>FastAPI Blog Team</p>
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