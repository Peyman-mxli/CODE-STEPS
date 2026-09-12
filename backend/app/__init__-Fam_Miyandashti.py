from flask import Flask
from app.config import Config
from app.extensions import db, jwt, limiter, migrate, mail

jwt_blocklist = set()


def create_app():
    flask_app = Flask(__name__)
    flask_app.config.from_object(Config)

    # -------------------------
    # Initialize extensions
    # -------------------------
    db.init_app(flask_app)
    jwt.init_app(flask_app)
    limiter.init_app(flask_app)
    migrate.init_app(flask_app, db)
    mail.init_app(flask_app)

    # Import models so migrations detect them
    import app.models

    # -------------------------
    # JWT BLOCKLIST CHECK
    # -------------------------
    @jwt.token_in_blocklist_loader
    def check_if_token_revoked(jwt_header, jwt_payload):
        jti = jwt_payload["jti"]
        return jti in jwt_blocklist

    # -------------------------
    # Import blueprints
    # -------------------------
    from app.routes.auth_routes import auth_bp
    from app.routes.admin_routes import admin_bp
    from app.routes.password_routes import password_bp
    from app.routes.course_routes import course_bp
    from app.routes.progress_routes import progress_bp
    from app.routes.dashboard_routes import dashboard_bp
    from app.routes.ai_routes import ai_bp
    from app.routes.code_routes import code_bp
    from app.routes.challenge_routes import challenge_bp
    from app.routes.certificate_routes import certificate_bp
    from app.routes.leaderboard_routes import leaderboard_bp
    from app.routes.user_routes import user_bp
    from app.routes.discussion_routes import discussion_bp

    # -------------------------
    # Register blueprints
    # -------------------------
    flask_app.register_blueprint(auth_bp)
    flask_app.register_blueprint(admin_bp)
    flask_app.register_blueprint(password_bp)
    flask_app.register_blueprint(course_bp)
    flask_app.register_blueprint(progress_bp)
    flask_app.register_blueprint(dashboard_bp)
    flask_app.register_blueprint(ai_bp)
    flask_app.register_blueprint(code_bp)
    flask_app.register_blueprint(challenge_bp)
    flask_app.register_blueprint(certificate_bp)
    flask_app.register_blueprint(leaderboard_bp)
    flask_app.register_blueprint(user_bp)
    flask_app.register_blueprint(discussion_bp)

    # -------------------------
    # Health check route
    # -------------------------
    @flask_app.route("/")
    def home():
        return {"message": "CodeSteps API is running"}

    return flask_app