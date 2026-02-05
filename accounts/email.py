import aiosmtplib
from email.message import EmailMessage
from accounts.security import SMTP_HOST, SMTP_PORT, SMTP_USER, SMTP_PASSWORD


async def send_email(to_email: str, subject: str, body: str):
    message = EmailMessage()
    message["From"] = SMTP_USER
    message["To"] = to_email
    message["Subject"] = subject
    message.set_content(body)

    try:
        await aiosmtplib.send(
            message,
            hostname=SMTP_HOST,
            port=SMTP_PORT,
            start_tls=True,
            username=SMTP_USER,
            password=SMTP_PASSWORD,
        )
        return True
    except Exception as e:
        print(f"Error while sending email: {e}")
        return False


async def send_verification_code(email: str, code: str):
    subject = "Email Verification Code"
    body = f"""
Hello!

Thank you for registering!

Your email verification code is: {code}

This code will expire in 15 minutes.

If you didn't request this, please ignore this email.

Best regards,
Instagram
    """
    return await send_email(email, subject, body)


async def send_reset_code(email: str, code: str):
    subject = "Password Reset Code"
    body = f"""
Hello!

You requested to reset your password.

Your password reset code is: {code}

This code will expire in 15 minutes.

If you didn't request this, please ignore this email.

Best regards,
Instagram
    """
    return await send_email(email, subject, body)