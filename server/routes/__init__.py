from routes.auth import CheckSession, Login, Logout, Signup
from routes.workouts import WorkoutById, Workouts


def register_resources(api):
    api.add_resource(Signup, "/signup")
    api.add_resource(Login, "/login")
    api.add_resource(Logout, "/logout")
    api.add_resource(CheckSession, "/check_session")
    api.add_resource(Workouts, "/workouts")
    api.add_resource(WorkoutById, "/workouts/<int:workout_id>")
