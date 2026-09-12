from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from datetime import datetime

from app.extensions import db
from app.models.user import User
from app.utils.password_reset_token import generate_password_reset_token, hash_reset_token
from app.utils.email_sender import send_password_reset_email


password_bp = Blueprint("password", __name__)


# -------------------------
# FORGOT PASSWORD
# -------------------------
@password_bp.route("/api/forgot-password", methods=["POST"])
def forgot_password():

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    email = data.get("email")

    if not email:
        return jsonify({"error": "Email is required"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        # Do not reveal if email exists (security)
        return jsonify({
            "message": "If the email exists, a reset link has been sent"
        }), 200

    # Generate reset token
    token, expires = generate_password_reset_token()

    # Hash token before storing in DB
    hashed_token = hash_reset_token(token)

    user.password_reset_token = hashed_token
    user.password_reset_expires = expires

    db.session.commit()

    # Temporarily store raw token on user object for email sending
    user.password_reset_token = token

    # Send email
    send_password_reset_email(user)

    return jsonify({
        "message": "If the email exists, a reset link has been sent"
    }), 200


# -------------------------
# RESET PASSWORD
# -------------------------
@password_bp.route("/api/reset-password/<token>", methods=["GET", "POST"])
def reset_password(token):

    # Hash incoming token to compare with DB
    hashed_token = hash_reset_token(token)

    user = User.query.filter_by(password_reset_token=hashed_token).first()

    if not user:
        return jsonify({"error": "Invalid reset token"}), 400

    if user.password_reset_expires and user.password_reset_expires < datetime.utcnow():
        return jsonify({"error": "Reset token expired"}), 400

    # If user opens link in browser
    if request.method == "GET":
        return jsonify({
            "message": "Reset token is valid. Send a POST request with a new password."
        }), 200

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    new_password = data.get("password")

    if not new_password:
        return jsonify({"error": "Password is required"}), 400

    # Basic password validation
    if len(new_password) < 6:
        return jsonify({
            "error": "Password must be at least 6 characters long"
        }), 400

    # Update password
    user.password_hash = generate_password_hash(new_password)

    # Clear reset token
    user.password_reset_token = None
    user.password_reset_expires = None

    db.session.commit()

    return jsonify({
        "message": "Password reset successful"
    }), 200