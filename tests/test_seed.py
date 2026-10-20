from seed import run_seed

from models import User, Workout


def test_seed_creates_starter_data(app):
    run_seed(app)

    with app.app_context():
        users = User.query.all()
        workouts = Workout.query.all()
        assert len(users) == 4
        assert len(workouts) == 24

        alex = User.query.filter_by(username="alex").one()
        assert alex.authenticate("password123")
        assert alex.workouts
        assert all(workout.user_id for workout in workouts)
        assert all(workout.name and workout.duration and workout.notes for workout in workouts)
