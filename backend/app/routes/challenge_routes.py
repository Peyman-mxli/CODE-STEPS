from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.challenge import Challenge
from app.models.user import User
from app.models.submission import Submission
from app.extensions import db, limiter
from app.utils.admin_required import admin_required
from app.services.code_evaluator import evaluate_submission
from app.services.plagiarism_service import check_plagiarism


challenge_bp = Blueprint("challenge", __name__)


# ------------------------------------------------
# GET ALL CHALLENGES
# ------------------------------------------------
@challenge_bp.route("/api/challenges", methods=["GET"])
def get_challenges():

    challenges = Challenge.query.all()

    return jsonify([
        c.to_dict() for c in challenges
    ]), 200


# ------------------------------------------------
# CREATE CHALLENGE (ADMIN ONLY)
# ------------------------------------------------
@challenge_bp.route("/api/challenges", methods=["POST"])
@jwt_required()
@admin_required()
def create_challenge():

    data = request.get_json()

    title = data.get("title")
    description = data.get("description")
    starter_code = data.get("starter_code")
    expected_output = data.get("expected_output")
    difficulty = data.get("difficulty", "easy")

    if not title or not expected_output:
        return jsonify({"error": "title and expected_output required"}), 400

    challenge = Challenge(
        title=title,
        description=description,
        starter_code=starter_code,
        expected_output=expected_output,
        difficulty=difficulty
    )

    db.session.add(challenge)
    db.session.commit()

    return jsonify({
        "message": "Challenge created",
        "challenge": challenge.to_dict()
    }), 201


# ------------------------------------------------
# SUBMIT SOLUTION
# ------------------------------------------------
@challenge_bp.route("/api/challenges/<int:challenge_id>/submit", methods=["POST"])
@jwt_required()
@limiter.limit("5/minute")
def submit_solution(challenge_id):

    challenge = Challenge.query.get(challenge_id)

    if not challenge:
        return jsonify({"error": "Challenge not found"}), 404

    data = request.get_json()
    code = data.get("code")

    if not code:
        return jsonify({"error": "Code required"}), 400

    if len(code) > 5000:
        return jsonify({"error": "Code too large"}), 400

    user_id = get_jwt_identity()
    user = User.query.get(user_id)

    try:

        evaluation = evaluate_submission(code)

        output = evaluation.get("stdout", "").strip()
        expected = challenge.expected_output.strip()

        success = output == expected

        xp_reward = 0

        if success:

            xp_reward = 20

            if challenge.difficulty == "medium":
                xp_reward = 40
            elif challenge.difficulty == "hard":
                xp_reward = 80

            user.add_xp(xp_reward)

        # plagiarism check
        plagiarism_matches = check_plagiarism(user.id, challenge.id, code)

        submission = Submission(
            user_id=user.id,
            challenge_id=challenge.id,
            code=code,
            status="passed" if success else "failed"
        )

        db.session.add(submission)
        db.session.commit()

        return jsonify({
            "success": success,
            "expected": expected,
            "your_output": output,
            "xp_rewarded": xp_reward,
            "plagiarism_matches": plagiarism_matches
        })

    except Exception as e:

        return jsonify({
            "error": str(e)
        }), 500


# ------------------------------------------------
# GET USER SUBMISSION HISTORY
# ------------------------------------------------
@challenge_bp.route("/api/submissions", methods=["GET"])
@jwt_required()
def get_my_submissions():

    user_id = get_jwt_identity()

    submissions = Submission.query.filter_by(user_id=user_id)\
        .order_by(Submission.created_at.desc()).all()

    results = []

    for s in submissions:

        challenge = Challenge.query.get(s.challenge_id)

        results.append({
            "id": s.id,
            "challenge_id": s.challenge_id,
            "challenge_title": challenge.title if challenge else None,
            "status": s.status,
            "created_at": s.created_at
        })

    return jsonify(results), 200


# ------------------------------------------------
# CHALLENGE LEADERBOARD
# ------------------------------------------------
@challenge_bp.route("/api/challenges/leaderboard", methods=["GET"])
def challenge_leaderboard():

    results = db.session.query(
        User.id,
        User.username,
        db.func.count(Submission.id).label("solved")
    ).join(
        Submission, Submission.user_id == User.id
    ).filter(
        Submission.status == "passed"
    ).group_by(
        User.id
    ).order_by(
        db.desc("solved")
    ).limit(20).all()

    leaderboard = []

    for r in results:
        leaderboard.append({
            "user_id": r.id,
            "username": r.username,
            "challenges_solved": r.solved
        })

    return jsonify(leaderboard), 200