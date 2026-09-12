from app import create_app
from app.extensions import db
from app.models.achievement import Achievement

app = create_app()

with app.app_context():

    achievements = [
        ("First Lesson", "Complete your first lesson", 20),
        ("10 Lessons", "Complete 10 lessons", 100),
        ("7 Day Streak", "Maintain a 7 day streak", 200),
        ("Level 5", "Reach level 5", 300),
    ]

    for name, desc, xp in achievements:

        exists = Achievement.query.filter_by(name=name).first()

        if not exists:
            db.session.add(
                Achievement(
                    name=name,
                    description=desc,
                    xp_reward=xp
                )
            )

    db.session.commit()

    print("Achievements seeded.")