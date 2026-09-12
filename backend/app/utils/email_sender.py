from flask_mail import Message
from flask import current_app
from app.extensions import mail


# -------------------------
# EMAIL VERIFICATION
# -------------------------
def send_verification_email(user):

    base_url = current_app.config.get("BASE_URL", "http://127.0.0.1:5000")

    verification_link = f"{base_url}/api/verify-email/{user.email_verification_token}"

    msg = Message(
        subject="Verify your CodeSteps account",
        recipients=[user.email]
    )

    msg.body = f"""
Hello {user.username},

Welcome to CodeSteps.

Please verify your email by clicking the link below:

{verification_link}

If you did not create this account, ignore this email.
"""

    mail.send(msg)


# -------------------------
# PASSWORD RESET EMAIL
# -------------------------
def send_password_reset_email(user):

    base_url = current_app.config.get("BASE_URL", "http://127.0.0.1:5000")

    reset_link = f"{base_url}/api/reset-password/{user.password_reset_token}"

    msg = Message(
        subject="Reset your CodeSteps password",
        recipients=[user.email]
    )

    msg.body = f"""
Hello {user.username},

We received a request to reset your password.

Click the link below to reset it:

{reset_link}

This link will expire in 1 hour.

If you did not request a password reset, ignore this email.
"""

    mail.send(msg)