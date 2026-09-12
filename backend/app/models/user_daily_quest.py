from datetime import datetime
from app.extensions import db


class UserDailyQuest(db.Model):

    __tablename__ = "user_daily_quests"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    quest_id = db.Column(
        db.Integer,
        db.ForeignKey("daily_quests.id"),
        nullable=False
    )

    progress = db.Column(
        db.Integer,
        default=0
    )

    completed = db.Column(
        db.Boolean,
        default=False
    )

    date = db.Column(
        db.Date,
        default=datetime.utcnow
    )