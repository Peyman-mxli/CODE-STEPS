from app.models.user import User


def generate_identification_id():

    last_user = User.query.order_by(User.id.desc()).first()

    if not last_user:
        return "a111302"

    last_code = last_user.identification_id

    number = int(last_code[1:])
    new_number = number + 1

    return f"a{new_number:06d}"