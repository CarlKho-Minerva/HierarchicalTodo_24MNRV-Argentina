import pytest
import sys
import os

# Add the parent directory to the Python path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from app import create_app, db
from app.models.user import User
from app.models.todo import TodoList, TodoItem
from flask_login import current_user


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


@pytest.fixture
def auth_client(client):
    # Register and login a test user
    client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password",
        },
    )
    client.post("/login", data={"username": "testuser", "password": "password"})
    return client


def test_create_list(auth_client):
    response = auth_client.post("/list/create", data={"title": "Test List"})
    assert response.status_code == 302
    todo_list = TodoList.query.filter_by(title="Test List").first()
    assert todo_list is not None
    assert todo_list.title == "Test List"


def test_create_item(auth_client):
    # First create a list
    auth_client.post("/list/create", data={"title": "Test List"})
    list_id = TodoList.query.filter_by(title="Test List").first().id

    # Then create an item in that list
    response = auth_client.post(
        "/item/create", data={"list_id": list_id, "title": "Test Item"}
    )
    assert response.status_code == 302
    todo_item = TodoItem.query.filter_by(title="Test Item").first()
    assert todo_item is not None
    assert todo_item.title == "Test Item"


def test_create_nested_item(auth_client):
    # Create list and parent item
    auth_client.post("/list/create", data={"title": "Test List"})
    list_id = TodoList.query.filter_by(title="Test List").first().id
    auth_client.post("/item/create", data={"list_id": list_id, "title": "Parent Item"})
    parent_id = TodoItem.query.filter_by(title="Parent Item").first().id

    # Create child item
    response = auth_client.post(
        "/item/create",
        data={"list_id": list_id, "parent_id": parent_id, "title": "Child Item"},
    )
    assert response.status_code == 302
    child_item = TodoItem.query.filter_by(title="Child Item").first()
    assert child_item is not None
    assert child_item.parent_id == parent_id
