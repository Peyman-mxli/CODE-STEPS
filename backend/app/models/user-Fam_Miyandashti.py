from datetime import datetime
from app.extensions import db


class User(db.Model):
    __tablename__ = "users"

    # -----------------------------
    # ROLES
    # -----------------------------
    ROLE_USER = "user"
    ROLE_VIP = "vip"
    ROLE_MODERATOR = "moderator"
    ROLE_ADMIN = "admin"

    id = db.Column(db.Integer, primary_key=True)

    identification_id = db.Column(db.String(20), unique=True, nullable=False)

    username = db.Column(db.String(50), unique=True, nullable=False)
    nickname = db.Column(db.String(50))

    email = db.Column(db.String(120), unique=True, nullable=False)
    phone = db.Column(db.String(20))
    country = db.Column(db.String(50))

    avatar = db.Column(db.String(255))

    password_hash = db.Column(db.String(255), nullable=False)

    role = db.Column(db.String(20), default=ROLE_USER)

    vip_status = db.Column(db.Boolean, default=False)

    is_banned = db.Column(db.Boolean, default=False)
    ban_reason = db.Column(db.String(255))

    is_active = db.Column(db.Boolean, default=True)

    # -----------------------------
    # GAMIFICATION SYSTEM
    # -----------------------------
    xp = db.Column(db.Integer, default=0)
    level = db.Column(db.Integer, default=1)

    streak_current = db.Column(db.Integer, default=0)
    streak_longest = db.Column(db.Integer, default=0)
    last_activity_date = db.Column(db.Date)

    # -----------------------------
    # EMAIL VERIFICATION
    # -----------------------------
    email_verified = db.Column(db.Boolean, default=False)

    email_verification_token = db.Column(
        db.String(255),
        nullable=True
    )

    email_verification_expires = db.Column(
        db.DateTime,
        nullable=True
    )

    # -----------------------------
    # PASSWORD RESET
    # -----------------------------
    password_reset_token = db.Column(
        db.String(255),
        nullable=True
    )

    password_reset_expires = db.Column(
        db.DateTime,
        nullable=True
    )

    # -----------------------------
    # CERTIFICATES
    # -----------------------------
    certificates = db.relationship(
        "Certificate",
        backref="owner",
        lazy=True
    )

    # -----------------------------
    # TIMESTAMPS
    # -----------------------------
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
    # ROLE HELPERS
    # -----------------------------
    def is_admin(self):
        return self.role == User.ROLE_ADMIN

    def is_moderator(self):
        return self.role == User.ROLE_MODERATOR

    def is_vip(self):
        return self.role == User.ROLE_VIP

    def is_user(self):
        return self.role == User.ROLE_USER

    def is_staff(self):
        return self.role in [User.ROLE_ADMIN, User.ROLE_MODERATOR]

    # -----------------------------
    # BAN SYSTEM
    # -----------------------------
    def ban(self, reason=None):
        self.is_banned = True
        self.ban_reason = reason

    def unban(self):
        self.is_banned = False
        self.ban_reason = None

    # -----------------------------
    # EMAIL VERIFY HELPER
    # -----------------------------
    def verify_email(self):
        self.email_verified = True
        self.email_verification_token = None
        self.email_verification_expires = None

    # -----------------------------
    # PASSWORD RESET HELPER
    # -----------------------------
    def clear_password_reset(self):
        self.password_reset_token = None
        self.password_reset_expires = None

    # -----------------------------
    # XP + LEVEL SYSTEM
    # -----------------------------
    def add_xp(self, amount):
        self.xp += amount

        while self.xp >= self.level * 100:
            self.level += 1

    def xp_to_next_level(self):
        return (self.level * 100) - self.xp

    # -----------------------------
    # RANK TITLE SYSTEM
    # -----------------------------
    def get_rank_title(self):

        if self.level >= 50:
            return "Grandmaster"
        elif self.level >= 30:
            return "Architect"
        elif self.level >= 20:
            return "Hacker"
        elif self.level >= 10:
            return "Coder"
        elif self.level >= 5:
            return "Apprentice"
        else:
            return "Beginner"

    # -----------------------------
    # STREAK SYSTEM
    # -----------------------------
    def update_streak(self, today):

        if self.last_activity_date is None:
            self.streak_current = 1
            self.last_activity_date = today
            return

        delta = (today - self.last_activity_date).days

        if delta == 0:
            return

        elif delta == 1:
            self.streak_current += 1

        else:
            self.streak_current = 1

        self.last_activity_date = today

        if self.streak_current > self.streak_longest:
            self.streak_longest = self.streak_current

    # -----------------------------
    # PROFILE STATS
    # -----------------------------
    def profile_stats(self):

        return {
            "xp": self.xp,
            "level": self.level,
            "rank_title": self.get_rank_title(),
            "xp_to_next_level": self.xp_to_next_level(),
            "streak_current": self.streak_current,
            "streak_longest": self.streak_longest
        }

    # -----------------------------
    # SERIALIZE USER
    # -----------------------------
    def to_dict(self):
        return {
            "id": self.id,
            "identification_id": self.identification_id,
            "username": self.username,
            "nickname": self.nickname,
            "email": self.email,
            "phone": self.phone,
            "country": self.country,
            "avatar": self.avatar,
            "role": self.role,
            "vip_status": self.vip_status,
            "is_banned": self.is_banned,
            "ban_reason": self.ban_reason,
            "is_active": self.is_active,
            "email_verified": self.email_verified,
            "xp": self.xp,
            "level": self.level,
            "rank_title": self.get_rank_title(),
            "xp_to_next_level": self.xp_to_next_level(),
            "streak_current": self.streak_current,
            "streak_longest": self.streak_longest,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }