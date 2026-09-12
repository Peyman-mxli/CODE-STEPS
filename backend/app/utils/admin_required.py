from functools import wraps
from flask_jwt_extended import jwt_required, get_jwt_identity
from flask import jsonify
from app.models.user import User


def admin_required():

    def wrapper(fn):
        @wraps(fn)
        @jwt_required()
        def decorator(*args, **kwargs):

            user_id = get_jwt_identity()

            user = User.query.get(int(user_id))

            if not user or user.role != User.ROLE_ADMIN:
                return jsonify({"error": "Admin access required"}), 403

            return fn(*args, **kwargs)

        return decorator

    return wrapper