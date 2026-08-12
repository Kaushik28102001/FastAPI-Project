import asyncio
from email.message import EmailMessage

import aiosmtplib
from config import settings


async def test_email():

    message = EmailMessage()

    message["From"] = "noreply@example.com"
    message["To"] = "YOUR_EMAIL@gmail.com"
    message["Subject"] = "Mailtrap Test"

    message.set_content(
        "This is a test email from my FastAPI project."
    )

    await aiosmtplib.send(
        message,
        hostname="sandbox.smtp.mailtrap.io",
        port=587,
        username=settings.mail_username,
        password=settings.mail_password,
        start_tls=True,
        timeout=30,
    )

    print("EMAIL SENT SUCCESSFULLY")


asyncio.run(test_email())