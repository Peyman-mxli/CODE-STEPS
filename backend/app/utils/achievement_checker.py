from app.extensions import db
from app.models.achievement import Achievement
from app.models.user_achievement import UserAchievement


def unlock_achievement(user, achievement_name):

    achievement = Achievement.query.filter_by(
        name=achievement_name
    ).first()

    if not achievement:
        return None

    existing = UserAchievement.query.filter_by(
        user_id=user.id,
        achievement_id=achievement.id
    ).first()

    if existing:
        return None

    unlocked = UserAchievement(
        user_id=user.id,
        achievement_id=achievement.id
    )

    db.session.add(unlocked)

    if achievement.xp_reward:
        user.add_xp(achievement.xp_reward)

    return achievement