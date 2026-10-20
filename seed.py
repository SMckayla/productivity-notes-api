#!/usr/bin/env python3
"""Create starter users and workouts."""

import os
import sys
from datetime import timedelta

from faker import Faker

SERVER_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "server")
if SERVER_DIR not in sys.path:
    sys.path.insert(0, SERVER_DIR)

from config import create_app, db
from models import User, Workout, utcnow

WORKOUT_NAMES = [
    "Easy Run",
    "Tempo Run",
    "Long Run",
    "Strength Circuit",
    "Upper Body Lift",
    "Lower Body Lift",
    "Yoga Flow",
    "Mobility",
    "Cycling",
    "Swim Laps",
    "Rowing Intervals",
    "HIIT",
]


def run_seed(app=None):
    app = app or create_app()
    fake = Faker()

    with app.app_context():
        db.create_all()
        db.session.query(Workout).delete()
        db.session.query(User).delete()
        db.session.commit()

        demo = User(username="alex")
        demo.password_hash = "password123"
        users = [demo]

        for index in range(1, 4):
            user = User(username=f"{fake.user_name()}_{index}"[:80])
            user.password_hash = "password123"
            users.append(user)

        db.session.add_all(users)
        db.session.commit()

        today = utcnow().date()
        for user in users:
            for offset in range(6):
                workout = Workout(
                    name=WORKOUT_NAMES[(user.id + offset) % len(WORKOUT_NAMES)],
                    duration=fake.random_int(min=20, max=90),
                    notes=fake.sentence(nb_words=8),
                    performed_on=today - timedelta(days=offset),
                    user_id=user.id,
                )
                db.session.add(workout)

        db.session.commit()
        print(f"Seeded {len(users)} users and {len(users) * 6} workouts.")
        print("Demo login: username 'alex' / password 'password123'")


if __name__ == "__main__":
    run_seed()
