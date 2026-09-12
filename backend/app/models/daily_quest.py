from app.extensions import db


class DailyQuest(db.Model):

    __tablename__ = "daily_quests"

    id = db.Column(db.Integer, primary_key=True)

    name = db.Column(
        db.String(100),
        nullable=False
    )

    description = db.Column(
        db.String(255),
        nullable=False
    )

    goal = db.Column(
        db.Integer,
        nullable=False
    )

    xp_reward = db.Column(
        db.Integer,
        default=0
    )