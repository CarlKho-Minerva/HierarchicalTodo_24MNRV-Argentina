import pytest
from app import create_app, db
from app.models.user import User
from app.models.todo import TodoList, TodoItem
from werkzeug.security import check_password_hash


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


def test_password_hashing():
    """Test that passwords are properly hashed"""
    u = User(username="test", email="test@example.com")
    u.set_password("password123")
    assert u.password_hash is not None
    assert u.password_hash != "password123"
    assert check_password_hash(u.password_hash, "password123")


def test_user_registration(client):
    """Test user registration process"""
    response = client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
        follow_redirects=True,
    )
    assert b"Registration successful" in response.data

    user = User.query.filter_by(username="testuser").first()
    assert user is not None
    assert user.email == "test@example.com"
    assert check_password_hash(user.password_hash, "password123")


def test_user_login_logout(client):
    """Test login and logout functionality"""
    # Register a user
    client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    # Test login
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "password123"},
        follow_redirects=True,
    )
    assert b"Medieval Todos" in response.data  # Successful login shows main page

    # Test logout
    response = client.get("/logout", follow_redirects=True)
    assert b"Login" in response.data  # Should be redirected to login page


def test_task_isolation(client):
    """Test that users can only see and modify their own tasks"""
    # Create two users
    client.post(
        "/register",
        data={
            "username": "user1",
            "email": "user1@example.com",
            "password": "password123",
        },
    )
    client.post(
        "/register",
        data={
            "username": "user2",
            "email": "user2@example.com",
            "password": "password123",
        },
    )

    # Login as user1 and create a list
    client.post("/login", data={"username": "user1", "password": "password123"})
    client.post("/list/create", data={"title": "User1 List"})
    client.get("/logout")

    # Login as user2 and try to access user1's list
    client.post("/login", data={"username": "user2", "password": "password123"})
    response = client.get("/")
    assert b"User1 List" not in response.data

    # Try to modify user1's list (assuming we know the list_id is 1)
    response = client.post("/list/1/edit", data={"title": "Hacked List"})
    assert response.status_code in [302, 403, 404]  # Should not be allowed

    # Verify the list title wasn't changed
    user1_list = TodoList.query.filter_by(title="User1 List").first()
    assert user1_list is not None
    assert user1_list.title == "User1 List"


def test_duplicate_username_registration(client):
    """Test that duplicate usernames are not allowed"""
    # Register first user
    client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test1@example.com",
            "password": "password123",
        },
    )

    # Try to register second user with same username
    response = client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test2@example.com",
            "password": "password123",
        },
        follow_redirects=True,
    )
    assert b"Username already taken" in response.data


def test_invalid_login_attempts(client):
    """Test that invalid login attempts are handled properly"""
    # Register a user
    client.post(
        "/register",
        data={
            "username": "testuser",
            "email": "test@example.com",
            "password": "password123",
        },
    )

    # Test wrong password
    response = client.post(
        "/login",
        data={"username": "testuser", "password": "wrongpassword"},
        follow_redirects=True,
    )
    assert b"Invalid username or password" in response.data

    # Test non-existent user
    response = client.post(
        "/login",
        data={"username": "nonexistent", "password": "password123"},
        follow_redirects=True,
    )
    assert b"Invalid username or password" in response.data
