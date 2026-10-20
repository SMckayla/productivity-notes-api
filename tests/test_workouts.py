from datetime import date, timedelta

from config import db
from models import User, Workout


def signup(client, username):
    response = client.post(
        "/signup",
        json={"username": username, "password": "secret123"},
    )
    assert response.status_code == 201
    return response.get_json()


def create_workout(client, **overrides):
    payload = {
        "name": "Easy Run",
        "duration": 30,
        "notes": "Felt good",
        "performed_on": "2026-10-20",
    }
    payload.update(overrides)
    return client.post("/workouts", json=payload)


def test_workout_routes_require_login(client):
    assert client.get("/workouts").status_code == 401
    assert client.post("/workouts", json={"name": "Run", "duration": 20}).status_code == 401
    assert client.get("/workouts/1").status_code == 401
    assert client.patch("/workouts/1", json={"name": "Walk"}).status_code == 401
    assert client.delete("/workouts/1").status_code == 401


def test_create_show_update_and_delete_workout(auth_client):
    created = create_workout(auth_client)
    assert created.status_code == 201
    body = created.get_json()
    assert body["name"] == "Easy Run"
    assert body["duration"] == 30
    assert body["notes"] == "Felt good"
    assert body["performed_on"] == "2026-10-20"
    assert body["user_id"] == 1
    workout_id = body["id"]

    shown = auth_client.get(f"/workouts/{workout_id}")
    assert shown.status_code == 200
    assert shown.get_json()["name"] == "Easy Run"

    updated = auth_client.patch(
        f"/workouts/{workout_id}",
        json={"duration": 45, "notes": "Added a hill"},
    )
    assert updated.status_code == 200
    assert updated.get_json()["duration"] == 45
    assert updated.get_json()["name"] == "Easy Run"

    deleted = auth_client.delete(f"/workouts/{workout_id}")
    assert deleted.status_code == 204
    assert auth_client.get(f"/workouts/{workout_id}").status_code == 404


def test_create_rejects_invalid_workout(auth_client):
    response = auth_client.post("/workouts", json={"name": " ", "duration": 0})
    assert response.status_code == 422
    assert "errors" in response.get_json()


def test_user_cannot_supply_another_owner(auth_client):
    response = create_workout(auth_client, user_id=999)
    assert response.status_code == 201
    assert response.get_json()["user_id"] == 1


def test_users_only_access_their_own_workouts(client):
    signup(client, "alex")
    mine = create_workout(client, name="Alex Run")
    workout_id = mine.get_json()["id"]
    client.delete("/logout")

    signup(client, "blair")
    create_workout(client, name="Blair Lift")

    listing = client.get("/workouts?per_page=10")
    assert listing.status_code == 200
    names = [item["name"] for item in listing.get_json()["workouts"]]
    assert names == ["Blair Lift"]

    assert client.get(f"/workouts/{workout_id}").status_code == 403
    assert client.patch(f"/workouts/{workout_id}", json={"name": "Stolen"}).status_code == 403
    assert client.delete(f"/workouts/{workout_id}").status_code == 403


def test_index_is_paginated(app, auth_client):
    with app.app_context():
        user = User.query.filter_by(username="runner").one()
        start = date(2026, 10, 1)
        for offset in range(12):
            db.session.add(
                Workout(
                    name=f"Session {offset}",
                    duration=20 + offset,
                    notes="seed",
                    performed_on=start + timedelta(days=offset),
                    user_id=user.id,
                )
            )
        db.session.commit()

    first = auth_client.get("/workouts?page=1&per_page=5")
    assert first.status_code == 200
    payload = first.get_json()
    assert payload["page"] == 1
    assert payload["per_page"] == 5
    assert payload["total"] == 12
    assert payload["pages"] == 3
    assert len(payload["workouts"]) == 5
    assert payload["workouts"][0]["name"] == "Session 11"

    second = auth_client.get("/workouts?page=2&per_page=5")
    assert len(second.get_json()["workouts"]) == 5
    third = auth_client.get("/workouts?page=3&per_page=5")
    assert len(third.get_json()["workouts"]) == 2


def test_missing_workout_returns_404(auth_client):
    assert auth_client.get("/workouts/999").status_code == 404
