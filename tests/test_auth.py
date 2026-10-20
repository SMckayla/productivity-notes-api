from config import db
from models import User


def test_signup_creates_user_and_starts_session(client):
    response = client.post(
        "/signup",
        json={"username": "ada", "password": "analytical"},
    )

    assert response.status_code == 201
    body = response.get_json()
    assert body["username"] == "ada"
    assert "id" in body
    assert "password" not in body
    assert "_password_hash" not in body

    session_response = client.get("/check_session")
    assert session_response.status_code == 200
    assert session_response.get_json()["username"] == "ada"


def test_signup_rejects_missing_fields(client):
    response = client.post("/signup", json={})
    assert response.status_code == 422
    assert "Username is required." in response.get_json()["errors"]
    assert "Password is required." in response.get_json()["errors"]


def test_signup_rejects_duplicate_username(client):
    first = client.post("/signup", json={"username": "ada", "password": "one"})
    assert first.status_code == 201

    client.delete("/logout")
    second = client.post("/signup", json={"username": "ada", "password": "two"})
    assert second.status_code == 422
    assert second.get_json()["errors"] == ["Username already exists."]


def test_password_is_hashed_and_not_readable(app, client):
    client.post("/signup", json={"username": "ada", "password": "analytical"})

    with app.app_context():
        user = User.query.filter_by(username="ada").first()
        assert user._password_hash != "analytical"
        assert user.authenticate("analytical")
        assert not user.authenticate("wrong")
        try:
            user.password_hash
            raised = False
        except AttributeError:
            raised = True
        assert raised


def test_login_and_check_session(client):
    client.post("/signup", json={"username": "ada", "password": "analytical"})
    client.delete("/logout")

    logged_out = client.get("/check_session")
    assert logged_out.status_code == 401

    login = client.post("/login", json={"username": "ada", "password": "analytical"})
    assert login.status_code == 200
    assert login.get_json()["username"] == "ada"

    checked = client.get("/check_session")
    assert checked.status_code == 200
    assert checked.get_json()["username"] == "ada"


def test_login_rejects_bad_password(client):
    client.post("/signup", json={"username": "ada", "password": "analytical"})
    client.delete("/logout")

    response = client.post(
        "/login",
        json={"username": "ada", "password": "nope"},
    )
    assert response.status_code == 401
    assert client.get("/check_session").status_code == 401


def test_logout_ends_session(client):
    client.post("/signup", json={"username": "ada", "password": "analytical"})

    logout = client.delete("/logout")
    assert logout.status_code == 204
    assert logout.data == b""
    assert client.get("/check_session").status_code == 401

    again = client.delete("/logout")
    assert again.status_code == 401


def test_username_uniqueness_is_enforced_by_the_database(app):
    with app.app_context():
        first = User(username="ada")
        first.password_hash = "one"
        second = User(username="ada")
        second.password_hash = "two"
        db.session.add(first)
        db.session.commit()
        db.session.add(second)
        try:
            db.session.commit()
            raised = False
        except Exception:
            db.session.rollback()
            raised = True
        assert raised
