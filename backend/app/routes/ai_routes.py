from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import limiter
from app.models.challenge import Challenge


ai_bp = Blueprint("ai", __name__)


# ------------------------------------------------
# BASIC AI QUESTION
# ------------------------------------------------
@ai_bp.route("/api/ai/ask", methods=["POST"])
@jwt_required()
@limiter.limit("10/minute")
def ask_ai():

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid body"}), 400

    question = data.get("question")

    if not question:
        return jsonify({"error": "Question required"}), 400

    answer = f"AI Tutor: You asked -> {question}"

    return jsonify({
        "question": question,
        "answer": answer
    }), 200


# ------------------------------------------------
# AI CODE EXPLAINER
# ------------------------------------------------
@ai_bp.route("/api/ai/explain", methods=["POST"])
@jwt_required()
@limiter.limit("10/minute")
def explain_code():

    data = request.get_json()

    code = data.get("code")

    if not code:
        return jsonify({"error": "Code is required"}), 400

    explanation = (
        "This code appears to run a sequence of instructions. "
        "A full AI explanation engine will analyze loops, variables, "
        "functions, and logic to explain what each part does."
    )

    return jsonify({
        "code": code,
        "explanation": explanation
    })


# ------------------------------------------------
# AI DEBUGGER
# ------------------------------------------------
@ai_bp.route("/api/ai/debug", methods=["POST"])
@jwt_required()
@limiter.limit("10/minute")
def debug_code():

    data = request.get_json()

    code = data.get("code")

    if not code:
        return jsonify({"error": "Code is required"}), 400

    result = {
        "analysis": "AI debugging system would analyze syntax errors, missing brackets, and logical mistakes.",
        "suggestion": "Check syntax and ensure all functions and parentheses are properly closed."
    }

    return jsonify({
        "code": code,
        "debug": result
    })


# ------------------------------------------------
# AI LEARNING HINTS
# ------------------------------------------------
@ai_bp.route("/api/ai/hint", methods=["POST"])
@jwt_required()
@limiter.limit("10/minute")
def learning_hint():

    data = request.get_json()

    question = data.get("question")

    if not question:
        return jsonify({"error": "Question required"}), 400

    hint = (
        "Think about breaking the problem into smaller steps. "
        "Try identifying inputs, outputs, and loops needed to solve the task."
    )

    return jsonify({
        "question": question,
        "hint": hint
    })


# ------------------------------------------------
# CHALLENGE AI HINT
# ------------------------------------------------
@ai_bp.route("/api/ai/challenge-hint/<int:challenge_id>", methods=["GET"])
@jwt_required()
@limiter.limit("10/minute")
def challenge_hint(challenge_id):

    challenge = Challenge.query.get(challenge_id)

    if not challenge:
        return jsonify({"error": "Challenge not found"}), 404

    hint = (
        f"Hint for challenge '{challenge.title}': "
        "Focus on the expected output and think about the logic required "
        "to transform the input into that result."
    )

    return jsonify({
        "challenge_id": challenge.id,
        "challenge_title": challenge.title,
        "hint": hint
    }), 200


# ------------------------------------------------
# AI CODE REVIEW
# ------------------------------------------------
@ai_bp.route("/api/ai/review", methods=["POST"])
@jwt_required()
@limiter.limit("10/minute")
def review_code():

    data = request.get_json()

    code = data.get("code")

    if not code:
        return jsonify({"error": "Code required"}), 400

    review = {
        "style": "Consider using meaningful variable names and consistent indentation.",
        "performance": "Check if loops or repeated operations can be optimized.",
        "security": "Ensure user inputs are validated and avoid executing unsafe code.",
        "suggestion": "Break large functions into smaller reusable functions."
    }

    return jsonify({
        "code": code,
        "review": review
    })