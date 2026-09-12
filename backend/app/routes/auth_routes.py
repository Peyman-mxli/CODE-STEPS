from flask_jwt_extended import (
    create_access_token,
    create_refresh_token,
    jwt_required,
    get_jwt_identity,
    get_jwt
)

from flask import Blueprint, request, jsonify
from app import db, limiter, jwt_blocklist
from app.models.user import User
from app.utils.security import check_user_not_banned
from app.utils.id_generator import generate_identification_id
from app.utils.email_token import generate_email_verification_token
from app.utils.email_sender import send_verification_email
from app.utils.rank_system import get_rank

from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename

from datetime import datetime
import os
import re

# 🔥 GOOGLE IMPORTS
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests

# 🔥 LOAD ENV
from dotenv import load_dotenv
load_dotenv()

GOOGLE_CLIENT_ID = os.getenv("GOOGLE_CLIENT_ID")

# ✅ PREFIX
auth_bp = Blueprint("auth", __name__, url_prefix="/api")

UPLOAD_FOLDER = "uploads"
os.makedirs(UPLOAD_FOLDER, exist_ok=True)


def is_valid_email(email):
    return re.match(r"[^@]+@[^@]+\.[^@]+", email)


# -------------------------
# REGISTER
# -------------------------
@auth_bp.route("/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():

    data = request.form

    first_name = data.get("first_name", "").strip()
    last_name = data.get("last_name", "").strip()
    username = data.get("username", "").strip().lower()
    email = data.get("email", "").strip().lower()
    phone = data.get("phone")
    country = data.get("country")

    password = data.get("password")
    confirm_password = data.get("confirm_password")

    file = request.files.get("avatar")
    avatar_path = None

    if file:
        filename = secure_filename(file.filename)
        filepath = os.path.join(UPLOAD_FOLDER, filename)
        file.save(filepath)
        avatar_path = filepath

    if not all([first_name, last_name, username, email, password, confirm_password]):
        return jsonify({"error": "Missing required fields"}), 400

    if password != confirm_password:
        return jsonify({"error": "Passwords do not match"}), 400

    if not is_valid_email(email):
        return jsonify({"error": "Invalid email format"}), 400

    if len(password) < 6:
        return jsonify({"error": "Password must be at least 6 characters"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    identification_id = generate_identification_id()
    password_hash = generate_password_hash(password)

    token, expires = generate_email_verification_token()

    new_user = User(
        identification_id=identification_id,
        username=username,
        email=email,
        password_hash=password_hash,
        role=User.ROLE_USER,
        first_name=first_name,
        last_name=last_name,
        phone=phone,
        country=country,
        avatar=avatar_path,
        email_verification_token=token,
        email_verification_expires=expires,
        email_verified=False
    )

    db.session.add(new_user)
    db.session.commit()

    try:
        send_verification_email(new_user)
    except Exception as e:
        print("EMAIL ERROR:", e)

    return jsonify({
        "message": "User registered. Check your email to verify."
    }), 201


# -------------------------
# VERIFY EMAIL
# -------------------------
@auth_bp.route("/verify-email/<token>", methods=["GET"])
def verify_email(token):

    user = User.query.filter_by(email_verification_token=token).first()

    if not user:
        return jsonify({"error": "Invalid verification token"}), 400

    if user.email_verification_expires and user.email_verification_expires < datetime.utcnow():
        return jsonify({"error": "Verification token expired"}), 400

    user.verify_email()
    db.session.commit()

    return jsonify({"message": "Email verified successfully"})


# -------------------------
# LOGIN
# -------------------------
@auth_bp.route("/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    username = data.get("username", "").strip().lower()
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    if user.is_banned:
        return jsonify({"error": "Account is banned"}), 403

    if not user.email_verified:
        return jsonify({"error": "Email not verified"}), 403

    if not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200


# -------------------------
# 🔥 GOOGLE LOGIN (FINAL FIX)
# -------------------------
@auth_bp.route("/google-login", methods=["POST"])
def google_login():

    data = request.get_json()
    token = data.get("token")

    if not token:
        return jsonify({"error": "Missing token"}), 400

    try:
        idinfo = id_token.verify_oauth2_token(
            token,
            google_requests.Request(),
            GOOGLE_CLIENT_ID
        )

        email = idinfo.get("email")
        first_name = idinfo.get("given_name", "")
        last_name = idinfo.get("family_name", "")

    except Exception as e:
        print("GOOGLE ERROR:", e)
        return jsonify({"error": "Invalid Google token"}), 400

    user = User.query.filter_by(email=email).first()

    if not user:
        user = User(
            identification_id=generate_identification_id(),
            username=email.split("@")[0],
            email=email,
            password_hash="google_oauth",
            role=User.ROLE_USER,
            first_name=first_name,
            last_name=last_name,
            email_verified=True
        )

        db.session.add(user)
        db.session.commit()

    access_token = create_access_token(identity=str(user.id))
    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "access_token": access_token,
        "refresh_token": refresh_token
    }), 200


# -------------------------
# USER XP
# -------------------------
@auth_bp.route("/user/xp", methods=["GET"])
@jwt_required()
def user_xp():

    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    rank = get_rank(user.level)

    return jsonify({
        "xp": user.xp,
        "level": user.level,
        "rank": rank
    }), 200


# -------------------------
# LOGOUT
# -------------------------
@auth_bp.route("/logout", methods=["POST"])
@jwt_required()
def logout():

    token = get_jwt()
    jti = token["jti"]

    jwt_blocklist.add(jti)

    return jsonify({"message": "Logout successful"}), 200