from datetime import date
from app.extensions import db
from app.models.daily_quest import DailyQuest
from app.models.user_daily_quest import UserDailyQuest


def update_daily_quests(user, xp_earned=0, lessons_completed=0):

    today = date.today()

    quests = DailyQuest.query.all()

    for quest in quests:

        user_quest = UserDailyQuest.query.filter_by(
            user_id=user.id,
            quest_id=quest.id,
            date=today
        ).first()

        if not user_quest:
            user_quest = UserDailyQuest(
                user_id=user.id,
                quest_id=quest.id,
                progress=0,
                completed=False,
                date=today
            )
            db.session.add(user_quest)

        # UPDATE PROGRESS
        if quest.quest_type == "lesson":
            user_quest.progress += lessons_completed

        if quest.quest_type == "xp":
            user_quest.progress += xp_earned

        # COMPLETE QUEST
        if not user_quest.completed and user_quest.progress >= quest.target:

            user_quest.completed = True

            user.xp += quest.xp_reward