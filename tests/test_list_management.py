import pytest
from app import create_app, db
from app.models.user import User
from app.models.todo import TodoList
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
def authenticated_client(client):
    # Register and login a test user
    client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )
    client.post("/login", data={"username": "testuser", "password": "password123"})
    return client


def test_create_list(authenticated_client):
    """Test creating a new todo list"""
    response = authenticated_client.post(
        "/list/create", data={"title": "Test List"}, follow_redirects=True
    )

    assert b"List created successfully!" in response.data
    todo_list = TodoList.query.filter_by(title="Test List").first()
    assert todo_list is not None
    assert todo_list.title == "Test List"


def test_create_multiple_lists(authenticated_client):
    """Test creating multiple todo lists"""
    list_titles = ["List 1", "List 2", "List 3"]

    for title in list_titles:
        response = authenticated_client.post(
            "/list/create", data={"title": title}, follow_redirects=True
        )
        assert b"List created successfully!" in response.data

    # Verify all lists were created
    lists = TodoList.query.all()
    assert len(lists) == 3
    assert set(l.title for l in lists) == set(list_titles)


def test_edit_list_name(authenticated_client):
    """Test editing a todo list's name"""
    # First create a list
    authenticated_client.post("/list/create", data={"title": "Original Title"})

    list_id = TodoList.query.filter_by(title="Original Title").first().id

    # Now edit the list name
    response = authenticated_client.post(
        f"/list/{list_id}/edit", data={"title": "Updated Title"}, follow_redirects=True
    )

    assert b"List name updated successfully!" in response.data
    updated_list = TodoList.query.get(list_id)
    assert updated_list.title == "Updated Title"


def test_delete_list(authenticated_client):
    """Test deleting a todo list"""
    # First create a list
    authenticated_client.post("/list/create", data={"title": "List to Delete"})

    list_id = TodoList.query.filter_by(title="List to Delete").first().id

    # Now delete the list
    response = authenticated_client.post(
        f"/list/{list_id}/delete", follow_redirects=True
    )

    assert b"List deleted successfully!" in response.data
    deleted_list = TodoList.query.get(list_id)
    assert deleted_list is None


def test_list_ownership(authenticated_client, client):
    """Test that users can only access their own lists"""
    # Create a list with the first user
    authenticated_client.post("/list/create", data={"title": "User 1 List"})

    # Get the list ID
    list_id = TodoList.query.filter_by(title="User 1 List").first().id

    # Logout first user
    authenticated_client.get("/logout")

    # Create and login second user
    client.post(
        "/register",
        data={
            "username": "testuser2",
            "email": "test2@example.com",
            "password": "password123",
        },
    )
    client.post("/login", data={"username": "testuser2", "password": "password123"})

    # Try to edit the first user's list
    response = client.post(
        f"/list/{list_id}/edit", data={"title": "Hacked Title"}, follow_redirects=True
    )

    assert b"Unauthorized action" in response.data
    original_list = TodoList.query.get(list_id)
    assert original_list.title == "User 1 List"


def test_empty_list_title(authenticated_client):
    """Test that empty list titles are not allowed"""
    response = authenticated_client.post(
        "/list/create", data={"title": ""}, follow_redirects=True
    )

    assert b"Title is required" in response.data
    empty_lists = TodoList.query.filter_by(title="").all()
    assert len(empty_lists) == 0


def test_duplicate_list_names_allowed(authenticated_client):
    """Test that users can create lists with the same name"""
    # Create first list
    authenticated_client.post("/list/create", data={"title": "My List"})

    # Create second list with same name
    response = authenticated_client.post(
        "/list/create", data={"title": "My List"}, follow_redirects=True
    )

    assert b"List created successfully!" in response.data
    duplicate_lists = TodoList.query.filter_by(title="My List").all()
    assert len(duplicate_lists) == 2
