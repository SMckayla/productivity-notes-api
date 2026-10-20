from flask import request, session
from flask_restful import Resource
from sqlalchemy.exc import IntegrityError

from config import db
from models import User
from schemas import user_schema


class Signup(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}
        username = data.get("username")
        password = data.get("password")

        errors = []
        if not isinstance(username, str) or not username.strip():
            errors.append("Username is required.")
        if not isinstance(password, str) or not password:
            errors.append("Password is required.")
        if errors:
            return {"errors": errors}, 422

        username = username.strip()
        if len(username) > 80:
            return {"errors": ["Username must be 80 characters or fewer."]}, 422

        if User.query.filter_by(username=username).first():
            return {"errors": ["Username already exists."]}, 422

        user = User(username=username)
        user.password_hash = password
        db.session.add(user)
        try:
            db.session.commit()
        except IntegrityError:
            db.session.rollback()
            return {"errors": ["Username already exists."]}, 422

        session.clear()
        session["user_id"] = user.id
        return user_schema.dump(user), 201


class Login(Resource):
    def post(self):
        data = request.get_json(silent=True) or {}
        username = data.get("username")
        password = data.get("password")

        if not isinstance(username, str) or not isinstance(password, str):
            return {"error": "Invalid username or password."}, 401

        user = User.query.filter_by(username=username.strip()).first()
        if not user or not user.authenticate(password):
            return {"error": "Invalid username or password."}, 401

        session.clear()
        session["user_id"] = user.id
        return user_schema.dump(user), 200


class Logout(Resource):
    def delete(self):
        if not session.get("user_id"):
            return {"error": "Unauthorized."}, 401

        session.pop("user_id", None)
        return "", 204


class CheckSession(Resource):
    def get(self):
        user_id = session.get("user_id")
        if not user_id:
            return {"error": "Unauthorized."}, 401

        user = db.session.get(User, user_id)
        if not user:
            session.pop("user_id", None)
            return {"error": "Unauthorized."}, 401

        return user_schema.dump(user), 200
