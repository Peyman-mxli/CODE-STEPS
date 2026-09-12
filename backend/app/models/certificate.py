from datetime import datetime
import uuid
from app.extensions import db


class Certificate(db.Model):
    __tablename__ = "certificates"

    id = db.Column(db.Integer, primary_key=True)

    certificate_id = db.Column(
        db.String(50),
        unique=True,
        nullable=False,
        default=lambda: "CERT-" + uuid.uuid4().hex[:10].upper()
    )

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    course_id = db.Column(
        db.Integer,
        db.ForeignKey("courses.id"),
        nullable=False
    )

    issued_at = db.Column(
        db.DateTime,
        default=datetime.utcnow
    )

    pdf_url = db.Column(
        db.String(255),
        nullable=True
    )

    # ✅ FIXED RELATIONSHIPS
    user = db.relationship(
        "User",
        back_populates="certificates"
    )

    course = db.relationship(
        "Course",
        backref="certificates"
    )

    def to_dict(self):
        return {
            "id": self.id,
            "certificate_id": self.certificate_id,
            "user_id": self.user_id,
            "course_id": self.course_id,
            "issued_at": self.issued_at.isoformat() if self.issued_at else None,
            "pdf_url": self.pdf_url
        }