from email.message import EmailMessage
import traceback

import aiosmtplib
from fastapi.templating import Jinja2Templates

from config import settings


# =========================================================
# JINJA TEMPLATES
# =========================================================

templates = Jinja2Templates(directory="templates")


# =========================================================
# SEND GENERAL EMAIL
# =========================================================

async def send_email(
    to_email: str,
    subject: str,
    plain_text: str,
    html_content: str | None = None,
) -> None:

    # -----------------------------------------------------
    # SMTP DEBUG INFORMATION
    # -----------------------------------------------------

    print("\n========== EMAIL DEBUG ==========")
    print("SMTP Server:", settings.mail_server)
    print("SMTP Port:", settings.mail_port)
    print("SMTP Username:", settings.mail_username)
    print("Mail From:", settings.mail_from)
    print("Mail To:", to_email)
    print("TLS:", settings.mail_use_tls)
    print("Password exists:", bool(settings.mail_password))
    print("=================================\n")

    # -----------------------------------------------------
    # CREATE EMAIL MESSAGE
    # -----------------------------------------------------

    message = EmailMessage()

    message["From"] = settings.mail_from
    message["To"] = to_email
    message["Subject"] = subject

    # Plain text version
    message.set_content(plain_text)

    # HTML version
    if html_content:
        message.add_alternative(
            html_content,
            subtype="html",
        )

    # -----------------------------------------------------
    # SEND EMAIL
    # -----------------------------------------------------

    try:

        print("Connecting and sending email...")

        result = await aiosmtplib.send(
            message,
            hostname=settings.mail_server,
            port=settings.mail_port,
            username=settings.mail_username,
            password=settings.mail_password,
            start_tls=settings.mail_use_tls,
            timeout=30,
        )

        print("\n========== EMAIL SUCCESS ==========")
        print("EMAIL SEND RESULT:", result)
        print("EMAIL SENT TO SMTP SUCCESSFULLY")
        print("Recipient:", to_email)
        print("===================================\n")

    except Exception as e:

        print("\n========== SMTP ERROR ==========")
        print("Error type:", type(e).__name__)
        print("Error:", str(e))

        traceback.print_exc()

        print("================================\n")

        raise


# =========================================================
# SEND OTP EMAIL
# =========================================================

async def send_otp_email(
    to_email: str,
    username: str,
    otp: str,
) -> None:

    subject = "Email Verification OTP - FastAPI Blog"

    # -----------------------------------------------------
    # PLAIN TEXT EMAIL
    # -----------------------------------------------------

    plain_text = f"""Hi {username},

Welcome to FastAPI Blog!

Hope you are doing well.

Thank you for registering with FastAPI Blog.

To complete your registration and verify your email address, please use the following One-Time Password (OTP):

OTP: {otp}

This OTP will expire in 5 minutes.

Please do not share this OTP with anyone for security reasons.

If you did not create an account on FastAPI Blog, please ignore this email.

Best regards,
FastAPI Blog Team
"""

    # -----------------------------------------------------
    # HTML EMAIL
    # -----------------------------------------------------

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Email Verification</title>
</head>

<body>

    <h2>Welcome to FastAPI Blog!</h2>

    <p>Hi <strong>{username}</strong>,</p>

    <p>Hope you are doing well.</p>

    <p>
        Thank you for registering with
        <strong>FastAPI Blog</strong>.
    </p>

    <p>
        To complete your registration and verify your email address,
        please use the following One-Time Password (OTP):
    </p>

    <h1>{otp}</h1>

    <p>
        This OTP will expire in <strong>5 minutes</strong>.
    </p>

    <p>
        Please do not share this OTP with anyone for security reasons.
    </p>

    <p>
        If you did not create an account on FastAPI Blog,
        please ignore this email.
    </p>

    <br>

    <p>
        Best regards,<br>
        <strong>FastAPI Blog Team</strong>
    </p>

</body>
</html>
"""

    # -----------------------------------------------------
    # SEND OTP EMAIL
    # -----------------------------------------------------

    await send_email(
        to_email=to_email,
        subject=subject,
        plain_text=plain_text,
        html_content=html_content,
    )


# =========================================================
# SEND PASSWORD RESET EMAIL
# =========================================================

async def send_password_reset_email(
    to_email: str,
    username: str,
    token: str,
) -> None:

    # -----------------------------------------------------
    # CREATE PASSWORD RESET URL
    # -----------------------------------------------------

    reset_url = (
        f"{settings.frontend_url}"
        f"/reset-password?token={token}"
    )

    subject = "Reset Your Password - FastAPI Blog"

    # -----------------------------------------------------
    # PLAIN TEXT EMAIL
    # -----------------------------------------------------

    plain_text = f"""Hi {username},

Hope you are doing well.

We received a request to reset the password for your FastAPI Blog account.

To reset your password, please click the link below:

{reset_url}

This password reset link will expire in 1 hour.

If you did not request a password reset, you can safely ignore this email. Your account will remain secure.

Best regards,
FastAPI Blog Team
"""

    # -----------------------------------------------------
    # HTML EMAIL
    # -----------------------------------------------------

    html_content = f"""
<!DOCTYPE html>
<html>
<head>
    <meta charset="UTF-8">
    <title>Reset Your Password</title>
</head>

<body>

    <h2>Password Reset Request</h2>

    <p>Hi <strong>{username}</strong>,</p>

    <p>Hope you are doing well.</p>

    <p>
        We received a request to reset the password for your
        <strong>FastAPI Blog</strong> account.
    </p>

    <p>
        Click the link below to reset your password:
    </p>

    <p>
        <a href="{reset_url}">
            Reset My Password
        </a>
    </p>

    <p>
        This password reset link will expire in
        <strong>1 hour</strong>.
    </p>

    <p>
        If you did not request a password reset,
        you can safely ignore this email.
        Your account will remain secure.
    </p>

    <br>

    <p>
        Best regards,<br>
        <strong>FastAPI Blog Team</strong>
    </p>

</body>
</html>
"""

    # -----------------------------------------------------
    # SEND PASSWORD RESET EMAIL
    # -----------------------------------------------------

    await send_email(
        to_email=to_email,
        subject=subject,
        plain_text=plain_text,
        html_content=html_content,
    )
