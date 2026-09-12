from datetime import datetime
from app.extensions import db


class Discussion(db.Model):
    __tablename__ = "discussions"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    content = db.Column(db.Text, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    replies = db.relationship(
        "DiscussionReply",
        backref="discussion",
        lazy=True,
        cascade="all, delete-orphan"
    )

    def to_dict(self):

        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "user_id": self.user_id,
            "created_at": self.created_at.isoformat(),
            "replies_count": len(self.replies)
        }


class DiscussionReply(db.Model):
    __tablename__ = "discussion_replies"

    id = db.Column(db.Integer, primary_key=True)

    content = db.Column(db.Text, nullable=False)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    discussion_id = db.Column(
        db.Integer,
        db.ForeignKey("discussions.id"),
        nullable=False
    )

    votes = db.Column(db.Integer, default=0)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):

        return {
            "id": self.id,
            "content": self.content,
            "user_id": self.user_id,
            "discussion_id": self.discussion_id,
            "votes": self.votes,
            "created_at": self.created_at.isoformat()
        }