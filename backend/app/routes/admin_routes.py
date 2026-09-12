from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required

from app.utils.admin_required import admin_required
from app.models.user import User
from app.models.course import Course
from app.models.enrollment import Enrollment
from app.models.certificate import Certificate
from app.extensions import db


admin_bp = Blueprint("admin", __name__)


# ------------------------------------------------
# GET USERS (Pagination + Search)
# ------------------------------------------------
@admin_bp.route("/api/admin/users", methods=["GET"])
@admin_required()
def get_users():

    page = request.args.get("page", 1, type=int)
    limit = request.args.get("limit", 10, type=int)
    search = request.args.get("search", "", type=str)

    query = User.query

    if search:
        query = query.filter(User.username.ilike(f"%{search}%"))

    users = query.paginate(page=page, per_page=limit, error_out=False)

    result = []

    for user in users.items:
        result.append({
            "id": user.id,
            "identification_id": user.identification_id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "xp": user.xp,
            "level": user.level,
            "is_banned": user.is_banned,
            "vip_status": user.vip_status
        })

    return jsonify({
        "users": result,
        "total_users": users.total,
        "page": users.page,
        "pages": users.pages
    })


# ------------------------------------------------
# BAN USER
# ------------------------------------------------
@admin_bp.route("/api/admin/ban-user", methods=["PATCH"])
@admin_required()
def ban_user():

    data = request.json
    target_user_id = data.get("user_id")
    reason = data.get("reason", "No reason provided")

    if not target_user_id:
        return jsonify({"error": "user_id is required"}), 400

    user = User.query.get(target_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.role == User.ROLE_ADMIN:
        return jsonify({"error": "Cannot ban another admin"}), 403

    user.ban(reason)

    db.session.commit()

    return jsonify({
        "message": "User banned successfully",
        "user_id": user.id,
        "reason": reason
    })


# ------------------------------------------------
# UNBAN USER
# ------------------------------------------------
@admin_bp.route("/api/admin/unban-user", methods=["PATCH"])
@admin_required()
def unban_user():

    data = request.json
    target_user_id = data.get("user_id")

    if not target_user_id:
        return jsonify({"error": "user_id is required"}), 400

    user = User.query.get(target_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user.unban()

    db.session.commit()

    return jsonify({
        "message": "User unbanned successfully",
        "user_id": user.id
    })


# ------------------------------------------------
# DELETE USER
# ------------------------------------------------
@admin_bp.route("/api/admin/delete-user", methods=["DELETE"])
@admin_required()
def delete_user():

    data = request.json
    target_user_id = data.get("user_id")

    if not target_user_id:
        return jsonify({"error": "user_id is required"}), 400

    user = User.query.get(target_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    if user.role == User.ROLE_ADMIN:
        return jsonify({"error": "Cannot delete an admin"}), 403

    db.session.delete(user)
    db.session.commit()

    return jsonify({
        "message": "User deleted successfully",
        "deleted_user_id": target_user_id
    })


# ------------------------------------------------
# PROMOTE USER
# ------------------------------------------------
@admin_bp.route("/api/admin/promote-user", methods=["PATCH"])
@admin_required()
def promote_user():

    data = request.json
    target_user_id = data.get("user_id")

    if not target_user_id:
        return jsonify({"error": "user_id is required"}), 400

    user = User.query.get(target_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user.role = User.ROLE_ADMIN

    db.session.commit()

    return jsonify({
        "message": "User promoted to admin successfully",
        "user_id": user.id
    })


# ------------------------------------------------
# DEMOTE USER
# ------------------------------------------------
@admin_bp.route("/api/admin/demote-user", methods=["PATCH"])
@admin_required()
def demote_user():

    data = request.json
    target_user_id = data.get("user_id")

    if not target_user_id:
        return jsonify({"error": "user_id is required"}), 400

    user = User.query.get(target_user_id)

    if not user:
        return jsonify({"error": "User not found"}), 404

    user.role = User.ROLE_USER

    db.session.commit()

    return jsonify({
        "message": "User demoted to normal user",
        "user_id": user.id
    })


# ------------------------------------------------
# ADMIN - LIST ALL COURSES
# ------------------------------------------------
@admin_bp.route("/api/admin/courses", methods=["GET"])
@admin_required()
def admin_list_courses():

    courses = Course.query.all()

    result = []

    for course in courses:

        enrollments = Enrollment.query.filter_by(course_id=course.id).count()
        certificates = Certificate.query.filter_by(course_id=course.id).count()

        result.append({
            "course_id": course.id,
            "title": course.title,
            "published": course.is_published,
            "students": enrollments,
            "certificates_issued": certificates
        })

    return jsonify(result)


# ------------------------------------------------
# ADMIN - DELETE COURSE
# ------------------------------------------------
@admin_bp.route("/api/admin/delete-course/<int:course_id>", methods=["DELETE"])
@admin_required()
def delete_course(course_id):

    course = Course.query.get(course_id)

    if not course:
        return jsonify({"error": "Course not found"}), 404

    db.session.delete(course)
    db.session.commit()

    return jsonify({
        "message": "Course deleted",
        "course_id": course_id
    })


# ------------------------------------------------
# ADMIN PLATFORM STATS
# ------------------------------------------------
@admin_bp.route("/api/admin/stats", methods=["GET"])
@admin_required()
def platform_stats():

    total_users = User.query.count()
    total_courses = Course.query.count()
    total_enrollments = Enrollment.query.count()
    total_certificates = Certificate.query.count()

    return jsonify({
        "total_users": total_users,
        "total_courses": total_courses,
        "total_enrollments": total_enrollments,
        "total_certificates": total_certificates
    })