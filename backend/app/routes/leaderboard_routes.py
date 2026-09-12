from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User


leaderboard_bp = Blueprint("leaderboard", __name__)


# ----------------------------------
# GLOBAL LEADERBOARD
# ----------------------------------
@leaderboard_bp.route("/api/leaderboard", methods=["GET"])
def global_leaderboard():

    users = User.query.order_by(User.xp.desc()).limit(50).all()

    result = []

    rank = 1

    for user in users:

        result.append({
            "rank": rank,
            "username": user.username,
            "xp": user.xp,
            "level": user.level,
            "streak": user.streak_current
        })

        rank += 1

    return jsonify(result), 200


# ----------------------------------
# MY RANK
# ----------------------------------
@leaderboard_bp.route("/api/leaderboard/me", methods=["GET"])
@jwt_required()
def my_rank():

    user_id = get_jwt_identity()

    users = User.query.order_by(User.xp.desc()).all()

    rank = 1

    for user in users:

        if user.id == user_id:

            return jsonify({
                "rank": rank,
                "username": user.username,
                "xp": user.xp,
                "level": user.level,
                "streak": user.streak_current
            }), 200

        rank += 1

    return jsonify({"error": "User not found"}), 404