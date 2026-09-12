import secrets
import hashlib
from datetime import datetime, timedelta


def generate_password_reset_token():
    """
    Generates a secure reset token and expiration time.
    The raw token will be sent to the user via email.
    """

    # Create secure random token
    token = secrets.token_urlsafe(32)

    # Token expires in 1 hour
    expires = datetime.utcnow() + timedelta(hours=1)

    return token, expires


def hash_reset_token(token):
    """
    Hash the reset token before storing it in the database.
    """
    return hashlib.sha256(token.encode()).hexdigest()