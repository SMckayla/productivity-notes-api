from datetime import date

from marshmallow import EXCLUDE, Schema, fields, pre_load, validate


class UserSchema(Schema):
    id = fields.Int(dump_only=True)
    username = fields.Str(required=True)

    class Meta:
        unknown = EXCLUDE


class WorkoutSchema(Schema):
    id = fields.Int(dump_only=True)
    name = fields.Str(required=True, validate=validate.Length(min=1, max=120))
    duration = fields.Int(required=True, validate=validate.Range(min=1, max=1440))
    notes = fields.Str(
        load_default=None,
        allow_none=True,
        validate=validate.Length(max=2000),
    )
    performed_on = fields.Date(load_default=date.today)
    user_id = fields.Int(dump_only=True)
    created_at = fields.DateTime(dump_only=True)

    class Meta:
        unknown = EXCLUDE

    @pre_load
    def clean_input(self, data, **kwargs):
        if not isinstance(data, dict):
            return data

        cleaned = dict(data)
        if isinstance(cleaned.get("name"), str):
            cleaned["name"] = cleaned["name"].strip()
        if isinstance(cleaned.get("notes"), str):
            cleaned["notes"] = cleaned["notes"].strip()

        duration = cleaned.get("duration")
        if isinstance(duration, str) and duration.isdigit():
            cleaned["duration"] = int(duration)

        if cleaned.get("performed_on") == "":
            cleaned.pop("performed_on")

        return cleaned


user_schema = UserSchema()
workout_schema = WorkoutSchema()
workouts_schema = WorkoutSchema(many=True)
