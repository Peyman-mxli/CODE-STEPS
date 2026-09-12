from datetime import datetime
from app.extensions import db


class Step(db.Model):
    __tablename__ = "steps"

    id = db.Column(db.Integer, primary_key=True)

    # Step info
    title = db.Column(db.String(150), nullable=False)
    content = db.Column(db.Text)

    # Optional video lesson
    video_url = db.Column(db.String(255))

    # Order inside the course
    step_order = db.Column(db.Integer, nullable=False)

    # Course relationship
    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id"),
        nullable=False
    )

    # Timestamps
    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    updated_at = db.Column(
        db.DateTime,
        default=datetime.utcnow,
        onupdate=datetime.utcnow
    )

    # -----------------------------
    # SERIALIZE
    # -----------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "content": self.content,
            "video_url": self.video_url,
            "step_order": self.step_order,
            "course_id": self.course_id,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }