from app.extensions import db
from app.models.achievement import Achievement
from app.models.user_achievement import UserAchievement
from app.models.progress import Progress
from app.models.user import User


def unlock_achievement(user, achievement_name):

    achievement = Achievement.query.filter_by(
        name=achievement_name
    ).first()

    if not achievement:
        return None

    already_unlocked = UserAchievement.query.filter_by(
        user_id=user.id,
        achievement_id=achievement.id
    ).first()

    if already_unlocked:
        return None

    unlocked = UserAchievement(
        user_id=user.id,
        achievement_id=achievement.id
    )

    user.xp += achievement.xp_reward

    db.session.add(unlocked)

    return achievement


def check_achievements(user):

    unlocked = []

    # TOTAL COMPLETED LESSONS
    completed_lessons = Progress.query.filter_by(
        user_id=user.id,
        completed=True
    ).count()

    # FIRST LESSON
    if completed_lessons >= 1:
        a = unlock_achievement(user, "First Lesson")
        if a:
            unlocked.append(a.name)

    # 10 LESSONS
    if completed_lessons >= 10:
        a = unlock_achievement(user, "10 Lessons")
        if a:
            unlocked.append(a.name)

    # 7 DAY STREAK
    if user.streak_current >= 7:
        a = unlock_achievement(user, "7 Day Streak")
        if a:
            unlocked.append(a.name)

    # LEVEL 5
    if user.level >= 5:
        a = unlock_achievement(user, "Level 5")
        if a:
            unlocked.append(a.name)

    return unlocked