import os


class Config:

    # -------------------------
    # CORE APP SETTINGS
    # -------------------------
    SECRET_KEY = os.getenv("SECRET_KEY", "dev-secret")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL",
        "sqlite:///codesteps.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # -------------------------
    # JWT CONFIG
    # -------------------------
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret")

    # -------------------------
    # EMAIL CONFIG (GMAIL SMTP)
    # -------------------------
    MAIL_SERVER = "smtp.gmail.com"
    MAIL_PORT = 587
    MAIL_USE_TLS = True
    MAIL_USE_SSL = False

    MAIL_USERNAME = os.getenv("MAIL_USERNAME")
    MAIL_PASSWORD = os.getenv("MAIL_PASSWORD")

    MAIL_DEFAULT_SENDER = os.getenv(
        "MAIL_DEFAULT_SENDER",
        "CodeSteps <no-reply@codesteps.dev>"
    )

    # -------------------------
    # 🔥 GOOGLE OAUTH CONFIG (NEW)
    # -------------------------
    GOOGLE_CLIENT_ID = os.getenv(
        "GOOGLE_CLIENT_ID",
        "1073078662901-e20m4f9b20dq9p35s823uedompgfg4g1.apps.googleusercontent.com"
    )