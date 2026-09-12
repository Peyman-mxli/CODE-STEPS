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

    MAIL_USERNAME = "mxli.peyman@gmail.com"
    MAIL_PASSWORD = "jtkn pxdf vzvv aunq"

    MAIL_DEFAULT_SENDER = "CodeSteps <mxli.peyman@gmail.com>"