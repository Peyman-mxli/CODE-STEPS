from app.extensions import db


class TestCase(db.Model):
    __tablename__ = "test_cases"

    id = db.Column(db.Integer, primary_key=True)

    challenge_id = db.Column(
        db.Integer,
        db.ForeignKey("challenges.id"),
        nullable=False
    )

    input_data = db.Column(db.Text, nullable=False)

    expected_output = db.Column(db.Text, nullable=False)

    is_hidden = db.Column(db.Boolean, default=True)

    created_at = db.Column(
        db.DateTime,
        server_default=db.func.now()
    )