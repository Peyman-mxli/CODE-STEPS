from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.user_achievement import UserAchievement
from app.models.achievement import Achievement
from app.models.certificate import Certificate


user_bp = Blueprint("users", __name__)


# ----------------------------------
# MY PROFILE
# ----------------------------------
@user_bp.route("/api/me", methods=["GET"])
@jwt_required()
def my_profile():

    user_id = get_jwt_identity()

    user = User.query.get(user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    return jsonify({
        "id": user.id,
        "username": user.username,
        "email": user.email,
        "role": user.role,
        "xp": user.xp,
        "level": user.level,
        "streak_current": user.streak_current,
        "streak_longest": user.streak_longest,
        "created_at": user.created_at.isoformat() if user.created_at else None
    }), 200


# ----------------------------------
# MY ACHIEVEMENTS
# ----------------------------------
@user_bp.route("/api/me/achievements", methods=["GET"])
@jwt_required()
def my_achievements():

    user_id = get_jwt_identity()

    user_achievements = UserAchievement.query.filter_by(
        user_id=user_id
    ).all()

    result = []

    for ua in user_achievements:

        achievement = Achievement.query.get(ua.achievement_id)

        if achievement:

            result.append({
                "title": achievement.title,
                "description": achievement.description,
                "unlocked_at": ua.unlocked_at.isoformat()
            })

    return jsonify(result), 200


# ----------------------------------
# MY CERTIFICATES
# ----------------------------------
@user_bp.route("/api/me/certificates", methods=["GET"])
@jwt_required()
def my_certificates():

    user_id = get_jwt_identity()

    certs = Certificate.query.filter_by(user_id=user_id).all()

    result = []

    for cert in certs:

        course = Course.query.get(cert.course_id)

        result.append({
            "certificate_id": cert.certificate_id,
            "course": course.title if course else "Unknown",
            "issued_at": cert.issued_at.isoformat() if cert.issued_at else None,
            "download_url": f"/api/certificate/download/{cert.certificate_id}"
        })

    return jsonify(result), 200


# ----------------------------------
# MY ENROLLED COURSES
# ----------------------------------
@user_bp.route("/api/me/courses", methods=["GET"])
@jwt_required()
def my_courses():

    user_id = get_jwt_identity()

    enrollments = Enrollment.query.filter_by(user_id=user_id).all()

    result = []

    for enrollment in enrollments:

        course = Course.query.get(enrollment.course_id)

        if course:

            result.append({
                "course_id": course.id,
                "title": course.title,
                "description": course.description
            })

    return jsonify(result), 200