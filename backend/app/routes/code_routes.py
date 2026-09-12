from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required
from app.extensions import limiter
from app.services.executor import run_code as execute_code

code_bp = Blueprint("code", __name__)


# ------------------------------------------------
# RUN USER CODE (Python Playground)
# ------------------------------------------------
@code_bp.route("/api/code/run", methods=["POST"])
@jwt_required()
@limiter.limit("5/minute")
def run_code():

    data = request.get_json()

    if not data:
        return jsonify({"error": "Invalid request"}), 400

    code = data.get("code")

    if not code:
        return jsonify({"error": "Code is required"}), 400

    # limit code size
    if len(code) > 5000:
        return jsonify({"error": "Code too large"}), 400

    try:

        # run code inside Docker sandbox
        result = execute_code(code)

        output = result.get("stdout", "")[:2000]
        error = result.get("stderr", "")[:2000]

        return jsonify({
            "success": True,
            "output": output,
            "error": error
        }), 200

    except Exception as e:

        return jsonify({
            "success": False,
            "error": str(e)
        }), 500