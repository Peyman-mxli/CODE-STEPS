from app import create_app, db
from app.models.user import User
from werkzeug.security import generate_password_hash
from app.utils.id_generator import generate_identification_id

app = create_app()

with app.app_context():

    username = "admin"
    email = "admin@codesteps.com"
    password = "admin123"

    existing = User.query.filter_by(username=username).first()

    if existing:
        print("Admin already exists")
    else:

        admin = User(
            identification_id=generate_identification_id(),
            username=username,
            email=email,
            password_hash=generate_password_hash(password),
            role=User.ROLE_ADMIN
        )

        db.session.add(admin)
        db.session.commit()

        print("Admin created")