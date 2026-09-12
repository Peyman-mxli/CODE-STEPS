from flask import Blueprint, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.course import Course
from app.models.step import Step
from app.models.progress import Progress

dashboard_bp = Blueprint("dashboard", __name__)


@dashboard_bp.route("/api/my-courses", methods=["GET"])
@jwt_required()
def my_courses():

    user_id = get_jwt_identity()

    courses = Course.query.all()

    result = []

    for course in courses:

        steps = Step.query.filter_by(course_id=course.id).all()
        total_steps = len(steps)

        if total_steps == 0:
            progress_percent = 0
        else:
            step_ids = [s.id for s in steps]

            completed = Progress.query.filter(
                Progress.user_id == user_id,
                Progress.step_id.in_(step_ids),
                Progress.completed == True
            ).count()

            progress_percent = int((completed / total_steps) * 100)

        result.append({
            "course_id": course.id,
            "title": course.title,
            "progress_percent": progress_percent
        })

    return jsonify(result), 200