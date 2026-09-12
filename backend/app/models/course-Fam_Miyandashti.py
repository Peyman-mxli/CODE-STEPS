from datetime import datetime
from app.extensions import db


class Course(db.Model):
    __tablename__ = "courses"

    id = db.Column(db.Integer, primary_key=True)

    # Course basic info
    title = db.Column(db.String(150), nullable=False)
    description = db.Column(db.Text)

    # Creator (admin or instructor)
    created_by = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    # Course status
    is_published = db.Column(db.Boolean, default=False)

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
    # RELATIONSHIPS
    # -----------------------------

    creator = db.relationship(
        "User",
        backref="courses_created"
    )

    steps = db.relationship(
        "Step",
        backref="course",
        cascade="all, delete-orphan",
        lazy=True
    )

    enrollments = db.relationship(
        "Enrollment",
        backref="course",
        cascade="all, delete-orphan",
        lazy=True
    )

    # -----------------------------
    # SERIALIZE
    # -----------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "created_by": self.created_by,
            "is_published": self.is_published,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }