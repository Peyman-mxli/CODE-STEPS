from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity

from app.models.discussion import Discussion, DiscussionReply
from app.extensions import db, limiter

discussion_bp = Blueprint("discussions", __name__)


# ------------------------------------------------
# GET ALL DISCUSSIONS
# ------------------------------------------------
@discussion_bp.route("/api/discussions", methods=["GET"])
def get_discussions():

    discussions = Discussion.query.order_by(Discussion.created_at.desc()).all()

    return jsonify([
        d.to_dict() for d in discussions
    ])


# ------------------------------------------------
# CREATE DISCUSSION
# ------------------------------------------------
@discussion_bp.route("/api/discussions", methods=["POST"])
@jwt_required()
@limiter.limit("5/minute")
def create_discussion():

    data = request.get_json()

    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return jsonify({"error": "title and content required"}), 400

    user_id = get_jwt_identity()

    discussion = Discussion(
        title=title,
        content=content,
        user_id=user_id
    )

    db.session.add(discussion)
    db.session.commit()

    return jsonify({
        "message": "Discussion created",
        "discussion": discussion.to_dict()
    }), 201


# ------------------------------------------------
# GET SINGLE DISCUSSION
# ------------------------------------------------
@discussion_bp.route("/api/discussions/<int:discussion_id>", methods=["GET"])
def get_discussion(discussion_id):

    discussion = Discussion.query.get(discussion_id)

    if not discussion:
        return jsonify({"error": "Discussion not found"}), 404

    replies = [
        r.to_dict() for r in discussion.replies
    ]

    return jsonify({
        "discussion": discussion.to_dict(),
        "replies": replies
    })


# ------------------------------------------------
# REPLY TO DISCUSSION
# ------------------------------------------------
@discussion_bp.route("/api/discussions/<int:discussion_id>/reply", methods=["POST"])
@jwt_required()
@limiter.limit("10/minute")
def reply_discussion(discussion_id):

    discussion = Discussion.query.get(discussion_id)

    if not discussion:
        return jsonify({"error": "Discussion not found"}), 404

    data = request.get_json()
    content = data.get("content")

    if not content:
        return jsonify({"error": "Reply content required"}), 400

    user_id = get_jwt_identity()

    reply = DiscussionReply(
        content=content,
        user_id=user_id,
        discussion_id=discussion_id
    )

    db.session.add(reply)
    db.session.commit()

    return jsonify({
        "message": "Reply posted",
        "reply": reply.to_dict()
    })


# ------------------------------------------------
# UPVOTE REPLY
# ------------------------------------------------
@discussion_bp.route("/api/discussions/reply/<int:reply_id>/vote", methods=["POST"])
@jwt_required()
def vote_reply(reply_id):

    reply = DiscussionReply.query.get(reply_id)

    if not reply:
        return jsonify({"error": "Reply not found"}), 404

    reply.votes += 1

    db.session.commit()

    return jsonify({
        "message": "Reply upvoted",
        "votes": reply.votes
    })