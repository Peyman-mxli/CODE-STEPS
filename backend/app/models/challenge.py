from datetime import datetime
from app.extensions import db


class Challenge(db.Model):
    __tablename__ = "challenges"

    id = db.Column(db.Integer, primary_key=True)

    title = db.Column(db.String(200), nullable=False)

    description = db.Column(db.Text, nullable=False)

    starter_code = db.Column(db.Text)

    expected_output = db.Column(db.Text)

    created_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "starter_code": self.starter_code,
            "expected_output": self.expected_output,
            "created_at": self.created_at.isoformat()
        }