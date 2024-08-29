from webapp.models import get_or_create, db, User


def get_or_create_user_id(user):
    # If user does not exist, create a new user in the "users" table
    user_hrc_id = user.get("id")
    user_exists = User.query.filter_by(hrc_id=user_hrc_id).first()
    if not user_exists:
        user_exists, _ = get_or_create(db.session,
                                       User,
                                       name=user.get("name"),
                                       email=user.get("email"),
                                       team=user.get("team"),
                                       department=user.get("department"),
                                       job_title=user.get("jobTitle"),
                                       hrc_id=user_hrc_id)

    return user_exists.id
