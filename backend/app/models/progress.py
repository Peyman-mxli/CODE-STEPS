from datetime import datetime
from app.extensions import db


class Progress(db.Model):
    __tablename__ = "progress"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    step_id = db.Column(
        db.Integer,
        db.ForeignKey("steps.id"),
        nullable=False
    )

    completed = db.Column(
        db.Boolean,
        default=True
    )

    completed_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    # Prevent duplicate progress records
    __table_args__ = (
        db.UniqueConstraint("user_id", "step_id", name="unique_user_step"),
    )

    # Relationships
    user = db.relationship("User", backref="progress_records")
    step = db.relationship("Step", backref="progress_records")

    # -----------------------------
    # SERIALIZE
    # -----------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "step_id": self.step_id,
            "completed": self.completed,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }