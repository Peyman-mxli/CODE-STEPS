from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from datetime import datetime, timedelta
import uuid

from app.extensions import db
from app.models.course import Course
from app.models.step import Step
from app.models.progress import Progress
from app.models.enrollment import Enrollment
from app.models.user import User
from app.models.certificate import Certificate

from app.services.achievement_service import check_achievements
from app.services.daily_quest_service import update_daily_quests

course_bp = Blueprint("courses", __name__)


# ----------------------------------
# GET ALL PUBLISHED COURSES
# ----------------------------------
@course_bp.route("/api/courses", methods=["GET"])
def get_courses():

    courses = Course.query.filter_by(is_published=True).all()

    return jsonify([
        course.to_dict() for course in courses
    ]), 200


# ----------------------------------
# GET SINGLE COURSE
# ----------------------------------
@course_bp.route("/api/courses/<int:course_id>", methods=["GET"])
def get_course(course_id):

    course = Course.query.get(course_id)

    if not course:
        return jsonify({
            "error": "Course not found"
        }), 404

    if not course.is_published:
        return jsonify({
            "error": "Course not published"
        }), 403

    return jsonify(course.to_dict()), 200


# ----------------------------------
# CREATE COURSE
# ----------------------------------
@course_bp.route("/api/courses", methods=["POST"])
@jwt_required()
def create_course():

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request body"}), 400

    title = data.get("title")
    description = data.get("description")

    if not title:
        return jsonify({"error": "Course title is required"}), 400

    user_id = get_jwt_identity()

    course = Course(
        title=title,
        description=description,
        created_by=user_id
    )

    db.session.add(course)
    db.session.commit()

    return jsonify({
        "message": "Course created successfully",
        "course": course.to_dict()
    }), 201


# ----------------------------------
# PUBLISH COURSE
# ----------------------------------
@course_bp.route("/api/courses/<int:course_id>/publish", methods=["PUT"])
@jwt_required()
def publish_course(course_id):

    course = Course.query.get(course_id)

    if not course:
        return jsonify({"error": "Course not found"}), 404

    course.is_published = True
    db.session.commit()

    return jsonify({
        "message": "Course published successfully",
        "course": course.to_dict()
    }), 200


# ----------------------------------
# CREATE STEP
# ----------------------------------
@course_bp.route("/api/courses/<int:course_id>/steps", methods=["POST"])
@jwt_required()
def create_step(course_id):

    course = Course.query.get(course_id)

    if not course:
        return jsonify({"error": "Course not found"}), 404

    data = request.get_json()

    title = data.get("title")
    content = data.get("content")
    video_url = data.get("video_url")
    step_order = data.get("step_order")

    if not title or step_order is None:
        return jsonify({"error": "title and step_order are required"}), 400

    step = Step(
        title=title,
        content=content,
        video_url=video_url,
        step_order=step_order,
        course_id=course_id
    )

    db.session.add(step)
    db.session.commit()

    return jsonify({
        "message": "Step created successfully",
        "step": step.to_dict()
    }), 201


# ----------------------------------
# GET COURSE STEPS
# ----------------------------------
@course_bp.route("/api/courses/<int:course_id>/steps", methods=["GET"])
@jwt_required()
def get_course_steps(course_id):

    user_id = get_jwt_identity()

    course = Course.query.get(course_id)

    if not course:
        return jsonify({"error": "Course not found"}), 404

    if not course.is_published:
        return jsonify({
            "error": "Course not published yet"
        }), 403

    enrollment = Enrollment.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()

    if not enrollment:
        return jsonify({
            "error": "You must enroll in this course first"
        }), 403

    steps = Step.query.filter_by(
        course_id=course_id
    ).order_by(Step.step_order).all()

    return jsonify([
        step.to_dict() for step in steps
    ]), 200


# ----------------------------------
# COMPLETE STEP
# ----------------------------------
@course_bp.route("/api/steps/<int:step_id>/complete", methods=["POST"])
@jwt_required()
def complete_step(step_id):

    user_id = get_jwt_identity()

    user = User.query.get(user_id)
    step = Step.query.get(step_id)

    if not step:
        return jsonify({"error": "Step not found"}), 404

    enrollment = Enrollment.query.filter_by(
        user_id=user_id,
        course_id=step.course_id
    ).first()

    if not enrollment:
        return jsonify({
            "error": "You must enroll in the course first"
        }), 403

    existing = Progress.query.filter_by(
        user_id=user_id,
        step_id=step_id
    ).first()

    if existing and existing.completed:
        return jsonify({
            "message": "Step already completed"
        }), 200

    if not existing:
        progress = Progress(
            user_id=user_id,
            step_id=step_id,
            completed=True
        )
        db.session.add(progress)
    else:
        existing.completed = True

    xp_reward = 50
    user.xp += xp_reward

    update_daily_quests(
        user,
        xp_earned=xp_reward,
        lessons_completed=1
    )

    if user.xp >= user.level * 100:
        user.level += 1

    today = datetime.utcnow().date()

    if user.last_activity_date:

        last_date = user.last_activity_date

        if last_date == today - timedelta(days=1):
            user.streak_current += 1

        elif last_date != today:
            user.streak_current = 1

    else:
        user.streak_current = 1

    if user.streak_current > user.streak_longest:
        user.streak_longest = user.streak_current

    user.last_activity_date = today

    unlocked = check_achievements(user)

    # -----------------------------
    # CERTIFICATE CHECK
    # -----------------------------
    course_id = step.course_id

    total_steps = Step.query.filter_by(course_id=course_id).count()

    completed_steps = (
        db.session.query(Progress)
        .join(Step, Progress.step_id == Step.id)
        .filter(
            Progress.user_id == user_id,
            Step.course_id == course_id,
            Progress.completed == True
        )
        .count()
    )

    if total_steps > 0 and completed_steps >= total_steps:

        existing_cert = Certificate.query.filter_by(
            user_id=user_id,
            course_id=course_id
        ).first()

        if not existing_cert:

            cert = Certificate(
                user_id=user_id,
                course_id=course_id,
                certificate_id="CERT-" + uuid.uuid4().hex[:10].upper()
            )

            db.session.add(cert)

    db.session.commit()

    return jsonify({
        "message": "Step completed",
        "xp_earned": xp_reward,
        "total_xp": user.xp,
        "level": user.level,
        "streak": user.streak_current,
        "achievements_unlocked": unlocked
    }), 200


# ----------------------------------
# GET COURSE PROGRESS
# ----------------------------------
@course_bp.route("/api/courses/<int:course_id>/progress", methods=["GET"])
@jwt_required()
def course_progress(course_id):

    user_id = get_jwt_identity()

    steps = Step.query.filter_by(course_id=course_id).all()

    total_steps = len(steps)

    if total_steps == 0:
        return jsonify({
            "course_id": course_id,
            "completed_steps": 0,
            "total_steps": 0,
            "progress_percent": 0
        }), 200

    step_ids = [step.id for step in steps]

    completed = Progress.query.filter(
        Progress.user_id == user_id,
        Progress.step_id.in_(step_ids),
        Progress.completed == True
    ).count()

    progress_percent = int((completed / total_steps) * 100)

    return jsonify({
        "course_id": course_id,
        "completed_steps": completed,
        "total_steps": total_steps,
        "progress_percent": progress_percent
    }), 200


# ----------------------------------
# ENROLL IN COURSE
# ----------------------------------
@course_bp.route("/api/courses/<int:course_id>/enroll", methods=["POST"])
@jwt_required()
def enroll_course(course_id):

    user_id = get_jwt_identity()

    course = Course.query.get(course_id)

    if not course:
        return jsonify({"error": "Course not found"}), 404

    if not course.is_published:
        return jsonify({
            "error": "Course not available yet"
        }), 403

    existing = Enrollment.query.filter_by(
        user_id=user_id,
        course_id=course_id
    ).first()

    if existing:
        return jsonify({"message": "Already enrolled"}), 200

    enrollment = Enrollment(
        user_id=user_id,
        course_id=course_id
    )

    db.session.add(enrollment)
    db.session.commit()

    return jsonify({
        "message": "Successfully enrolled",
        "course_id": course_id
    }), 201