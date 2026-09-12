import secrets
from datetime import datetime, timedelta


def generate_email_verification_token():

    token = secrets.token_urlsafe(32)

    expires = datetime.utcnow() + timedelta(hours=24)

    return token, expires