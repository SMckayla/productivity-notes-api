import os
import tempfile

import pytest

from config import create_app, db


@pytest.fixture(scope="session")
def app():
    db_fd, db_path = tempfile.mkstemp(suffix=".db")
    os.close(db_fd)
    application = create_app(
        {
            "TESTING": True,
            "SQLALCHEMY_DATABASE_URI": "sqlite:///" + db_path,
            "SECRET_KEY": "test-secret",
        }
    )
    yield application
    if os.path.exists(db_path):
        os.remove(db_path)


@pytest.fixture(autouse=True)
def clean_db(app):
    with app.app_context():
        db.create_all()
        yield
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


@pytest.fixture
def auth_client(client):
    response = client.post(
        "/signup",
        json={"username": "runner", "password": "secret123"},
    )
    assert response.status_code == 201
    return client
