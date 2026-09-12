from datetime import datetime
from app.extensions import db


class LessonCompletion(db.Model):

    __tablename__ = "lesson_completions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    lesson_id = db.Column(
        db.String(100),
        nullable=False
    )

    xp_awarded = db.Column(
        db.Integer,
        default=50
    )

    completed_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )