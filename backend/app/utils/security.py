from flask_jwt_extended import get_jwt_identity
from app.models.user import User


def get_current_user():

    user_id = get_jwt_identity()

    if not user_id:
        return None

    return User.query.get(int(user_id))


def check_user_not_banned():

    user = get_current_user()

    if not user:
        return False, {"error": "User not found"}

    if user.is_banned:
        return False, {
            "error": "Account is banned",
            "reason": user.ban_reason
        }

    return True, user


def require_admin():

    user = get_current_user()

    if not user:
        return False, {"error": "User not found"}

    if user.role != User.ROLE_ADMIN:
        return False, {"error": "Admin access required"}

    return True, user