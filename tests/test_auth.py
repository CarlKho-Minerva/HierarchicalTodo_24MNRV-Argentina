import pytest
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from app import create_app, db
from app.models.user import User


@pytest.fixture
def app():
    app = create_app("config.TestConfig")
    with app.app_context():
        db.create_all()
        yield app
        db.session.remove()
        db.drop_all()


@pytest.fixture
def client(app):
    return app.test_client()


def test_register(client):
    response = client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password",
        },
        follow_redirects=True,
    )
    assert b"Registration successful!" in response.data
    assert User.query.filter_by(username="testuser").first() is not None


def test_login(client):
    # First register a user
    client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password",
        },
    )

    # Then try to login
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "password"},
        follow_redirects=True,
    )
    assert b"Medieval Todos" in response.data  # Check if redirected to main page
