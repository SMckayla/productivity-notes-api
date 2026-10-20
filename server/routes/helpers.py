from flask import session

from config import db
from models import User, Workout


def require_user():
    """Return the logged-in user, or a 401 response tuple."""
    user_id = session.get("user_id")
    if not user_id:
        return None, ({"error": "Unauthorized."}, 401)

    user = db.session.get(User, user_id)
    if not user:
        session.pop("user_id", None)
        return None, ({"error": "Unauthorized."}, 401)

    return user, None


def owned_workout_or_error(user, workout_id):
    """Return a workout owned by user, or a 404/403 response tuple."""
    workout = db.session.get(Workout, workout_id)
    if workout is None:
        return None, ({"error": "Workout not found."}, 404)
    if workout.user_id != user.id:
        return None, ({"error": "Forbidden."}, 403)
    return workout, None


def pagination_args():
    from flask import request

    page = request.args.get("page", default=1, type=int) or 1
    per_page = request.args.get("per_page", default=5, type=int) or 5
    return max(page, 1), min(max(per_page, 1), 20)
