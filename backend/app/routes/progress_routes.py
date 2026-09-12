from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.extensions import db
from app.models.progress import Progress
from app.models.step import Step
from app.models.certificate import Certificate
from app.models.course import Course

import uuid

progress_bp = Blueprint("progress", __name__)


# COMPLETE STEP
@progress_bp.route("/api/progress/complete-step", methods=["POST"])
@jwt_required()
def complete_step():

    user_id = get_jwt_identity()
    data = request.get_json()

    step_id = data.get("step_id")

    if not step_id:
        return jsonify({"error": "step_id is required"}), 400

    step = Step.query.get(step_id)

    if not step:
        return jsonify({"error": "Step not found"}), 404

    # Check if already completed
    progress = Progress.query.filter_by(
        user_id=user_id,
        step_id=step_id
    ).first()

    if progress:
        return jsonify({"message": "Step already completed"}), 200

    # Save progress
    progress = Progress(
        user_id=user_id,
        step_id=step_id
    )

    db.session.add(progress)
    db.session.commit()

    # -------------------------
    # CHECK COURSE COMPLETION
    # -------------------------

    course_id = step.course_id

    total_steps = Step.query.filter_by(
        course_id=course_id
    ).count()

    completed_steps = (
        db.session.query(Progress)
        .join(Step, Progress.step_id == Step.id)
        .filter(
            Progress.user_id == user_id,
            Step.course_id == course_id
        )
        .count()
    )

    # If all steps completed → create certificate
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

    return jsonify({"message": "Step completed"}), 201


# GET MY PROGRESS
@progress_bp.route("/api/progress/my-progress", methods=["GET"])
@jwt_required()
def my_progress():

    user_id = get_jwt_identity()

    progress = Progress.query.filter_by(
        user_id=user_id
    ).all()

    return jsonify([p.to_dict() for p in progress]), 200