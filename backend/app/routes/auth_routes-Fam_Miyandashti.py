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

from datetime import datetime


auth_bp = Blueprint("auth", __name__)

# -------------------------
# REGISTER
# -------------------------

@auth_bp.route("/api/register", methods=["POST"])
@limiter.limit("5 per minute")
def register():

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    username = data.get("username")
    email = data.get("email")
    password = data.get("password")

    if not username or not email or not password:
        return jsonify({"error": "Missing required fields"}), 400

    if User.query.filter_by(username=username).first():
        return jsonify({"error": "Username already exists"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 400

    identification_id = generate_identification_id()
    password_hash = generate_password_hash(password)

    # Generate verification token
    token, expires = generate_email_verification_token()

    new_user = User(
        identification_id=identification_id,
        username=username,
        email=email,
        password_hash=password_hash,
        role=User.ROLE_USER,
        email_verification_token=token,
        email_verification_expires=expires
    )

    db.session.add(new_user)
    db.session.commit()

    send_verification_email(new_user)

    return jsonify({
        "message": "User registered successfully. Please verify your email.",
        "identification_id": identification_id
    }), 201


# -------------------------
# VERIFY EMAIL
# -------------------------

@auth_bp.route("/api/verify-email/<token>", methods=["GET"])
def verify_email(token):

    user = User.query.filter_by(email_verification_token=token).first()

    if not user:
        return jsonify({"error": "Invalid verification token"}), 400

    if user.email_verification_expires and user.email_verification_expires < datetime.utcnow():
        return jsonify({"error": "Verification token expired"}), 400

    user.verify_email()
    db.session.commit()

    return jsonify({
        "message": "Email verified successfully"
    })


# -------------------------
# LOGIN
# -------------------------

@auth_bp.route("/api/login", methods=["POST"])
@limiter.limit("5 per minute")
def login():

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    username = data.get("username")
    password = data.get("password")

    if not username or not password:
        return jsonify({"error": "Missing credentials"}), 400

    user = User.query.filter_by(username=username).first()

    if not user:
        return jsonify({"error": "Invalid username or password"}), 401

    if user.is_banned:
        return jsonify({
            "error": "Account is banned",
            "reason": user.ban_reason
        }), 403

    if not user.email_verified:
        return jsonify({
            "error": "Email not verified"
        }), 403

    if not check_password_hash(user.password_hash, password):
        return jsonify({"error": "Invalid username or password"}), 401

    access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    refresh_token = create_refresh_token(identity=str(user.id))

    return jsonify({
        "message": "Login successful",
        "access_token": access_token,
        "refresh_token": refresh_token,
        "user": {
            "id": user.id,
            "username": user.username,
            "identification_id": user.identification_id,
            "role": user.role
        }
    }), 200


# -------------------------
# REFRESH TOKEN
# -------------------------

@auth_bp.route("/api/refresh", methods=["POST"])
@jwt_required(refresh=True)
def refresh():

    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    new_access_token = create_access_token(
        identity=str(user.id),
        additional_claims={"role": user.role}
    )

    return jsonify({
        "access_token": new_access_token
    })


# -------------------------
# LOGOUT
# -------------------------

@auth_bp.route("/api/logout", methods=["POST"])
@jwt_required()
def logout():

    token = get_jwt()
    jti = token["jti"]

    jwt_blocklist.add(jti)

    return jsonify({
        "message": "Logout successful"
    }), 200


# -------------------------
# UPDATE PROFILE
# -------------------------

@auth_bp.route("/api/profile/update", methods=["PATCH"])
@jwt_required()
def update_profile():

    allowed, result = check_user_not_banned()

    if not allowed:
        return jsonify(result), 403

    user = result
    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    nickname = data.get("nickname")
    phone = data.get("phone")
    country = data.get("country")
    avatar = data.get("avatar")

    if nickname is not None:
        user.nickname = nickname

    if phone is not None:
        user.phone = phone

    if country is not None:
        user.country = country

    if avatar is not None:
        user.avatar = avatar

    db.session.commit()

    return jsonify({
        "message": "Profile updated successfully",
        "user": {
            "id": user.id,
            "username": user.username,
            "nickname": user.nickname,
            "phone": user.phone,
            "country": user.country,
            "avatar": user.avatar
        }
    })


# -------------------------
# USER XP + LEVEL + RANK
# -------------------------

@auth_bp.route("/api/user/xp", methods=["GET"])
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
# GLOBAL LEADERBOARD
# -------------------------

@auth_bp.route("/api/leaderboard", methods=["GET"])
def leaderboard():

    users = User.query.order_by(User.xp.desc()).limit(10).all()

    leaderboard_data = []

    for user in users:
        leaderboard_data.append({
            "username": user.username,
            "level": user.level,
            "xp": user.xp,
            "rank": get_rank(user.level)
        })

    return jsonify(leaderboard_data), 200
# -------------------------
# XP REWARD SYSTEM
# -------------------------

@auth_bp.route("/api/xp/reward", methods=["POST"])
@jwt_required()
def reward_xp():

    user_id = get_jwt_identity()
    user = db.session.get(User, user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    xp_amount = data.get("xp", 0)

    if xp_amount <= 0:
        return jsonify({"error": "Invalid XP amount"}), 400

    # Add XP
    user.add_xp(xp_amount)

    # Update streak
    today = datetime.utcnow().date()
    user.update_streak(today)

    db.session.commit()

    rank = get_rank(user.level)

    return jsonify({
        "message": "XP rewarded",
        "xp_gained": xp_amount,
        "total_xp": user.xp,
        "level": user.level,
        "rank": rank,
        "streak_current": user.streak_current,
        "streak_longest": user.streak_longest
    }), 200