from flask import request
from flask_restful import Resource
from marshmallow import ValidationError

from config import db
from models import Workout
from routes.helpers import owned_workout_or_error, pagination_args, require_user
from schemas import workout_schema, workouts_schema


class Workouts(Resource):
    def get(self):
        user, error = require_user()
        if error:
            return error

        page, per_page = pagination_args()
        stmt = (
            db.select(Workout)
            .where(Workout.user_id == user.id)
            .order_by(Workout.performed_on.desc(), Workout.id.desc())
        )
        pagination = db.paginate(stmt, page=page, per_page=per_page, error_out=False)

        return {
            "workouts": workouts_schema.dump(pagination.items),
            "page": pagination.page,
            "per_page": pagination.per_page,
            "total": pagination.total,
            "pages": pagination.pages,
        }, 200

    def post(self):
        user, error = require_user()
        if error:
            return error

        try:
            payload = workout_schema.load(request.get_json(silent=True) or {})
        except ValidationError as err:
            return {"errors": err.messages}, 422

        workout = Workout(user_id=user.id, **payload)
        db.session.add(workout)
        db.session.commit()
        return workout_schema.dump(workout), 201


class WorkoutById(Resource):
    def get(self, workout_id):
        user, error = require_user()
        if error:
            return error

        workout, error = owned_workout_or_error(user, workout_id)
        if error:
            return error

        return workout_schema.dump(workout), 200

    def patch(self, workout_id):
        user, error = require_user()
        if error:
            return error

        workout, error = owned_workout_or_error(user, workout_id)
        if error:
            return error

        try:
            payload = workout_schema.load(
                request.get_json(silent=True) or {},
                partial=True,
            )
        except ValidationError as err:
            return {"errors": err.messages}, 422

        for key, value in payload.items():
            setattr(workout, key, value)

        db.session.commit()
        return workout_schema.dump(workout), 200

    def delete(self, workout_id):
        user, error = require_user()
        if error:
            return error

        workout, error = owned_workout_or_error(user, workout_id)
        if error:
            return error

        db.session.delete(workout)
        db.session.commit()
        return "", 204
