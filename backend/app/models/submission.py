from app.extensions import db


class Submission(db.Model):
    __tablename__ = "submissions"

    id = db.Column(db.Integer, primary_key=True)

    user_id = db.Column(
        db.Integer,
        db.ForeignKey("users.id"),
        nullable=False
    )

    challenge_id = db.Column(
        db.Integer,
        db.ForeignKey("challenges.id"),
        nullable=False
    )

    code = db.Column(db.Text, nullable=False)

    status = db.Column(db.String(20), nullable=False)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )