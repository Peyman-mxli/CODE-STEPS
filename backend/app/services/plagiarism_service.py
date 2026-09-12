from difflib import SequenceMatcher
from app.models.submission import Submission


def similarity(a, b):
    return SequenceMatcher(None, a, b).ratio()


def check_plagiarism(user_id, challenge_id, code):

    submissions = Submission.query.filter(
        Submission.challenge_id == challenge_id,
        Submission.user_id != user_id
    ).all()

    suspicious = []

    for s in submissions:

        score = similarity(code, s.code)

        if score > 0.8:

            suspicious.append({
                "submission_id": s.id,
                "user_id": s.user_id,
                "similarity": round(score, 2)
            })

    return suspicious