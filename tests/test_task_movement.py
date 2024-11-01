import pytest
from app import create_app, db
from app.models.user import User
from app.models.todo import TodoList, TodoItem


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
    """Create a test user and authenticate the client"""
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


@pytest.fixture
def setup_lists_and_tasks(authenticated_client):
    """Setup test lists and tasks"""
    # Create two lists
    authenticated_client.post("/list/create", data={"title": "List 1"})
    authenticated_client.post("/list/create", data={"title": "List 2"})

    # Create tasks in List 1
    authenticated_client.post("/item/create", data={"list_id": 1, "title": "Task 1"})
    authenticated_client.post("/item/create", data={"list_id": 1, "title": "Task 2"})

    # Create a parent task with children
    authenticated_client.post(
        "/item/create", data={"list_id": 1, "title": "Parent Task"}
    )
    authenticated_client.post(
        "/item/create",
        data={"list_id": 1, "parent_id": 3, "title": "Child Task 1"},
    )
    authenticated_client.post(
        "/item/create",
        data={"list_id": 1, "parent_id": 3, "title": "Child Task 2"},
    )

    return authenticated_client


def test_move_top_level_task(setup_lists_and_tasks):
    """Test moving a top-level task between lists"""
    client = setup_lists_and_tasks

    # Move Task 1 from List 1 to List 2
    response = client.post(
        "/item/1/move",
        data={"list_id": 2},
        follow_redirects=True,
    )
    assert b"Item moved successfully" in response.data

    # Verify task was moved
    moved_task = TodoItem.query.get(1)
    assert moved_task.list_id == 2
    assert moved_task.parent_id is None


def test_move_nested_task_as_top_level(setup_lists_and_tasks):
    """Test moving a nested task as a top-level task in another list"""
    client = setup_lists_and_tasks

    # Move Child Task 1 to List 2 as top-level task
    response = client.post(
        "/item/4/move",
        data={"list_id": 2},
        follow_redirects=True,
    )
    assert b"Item moved successfully" in response.data

    # Verify task was moved and is now top-level
    moved_task = TodoItem.query.get(4)
    assert moved_task.list_id == 2
    assert moved_task.parent_id is None


def test_move_parent_task_with_children(setup_lists_and_tasks):
    """Test moving a parent task with its children to another list"""
    client = setup_lists_and_tasks

    # Move Parent Task to List 2
    response = client.post(
        "/item/3/move",
        data={"list_id": 2},
        follow_redirects=True,
    )
    assert b"Item moved successfully" in response.data

    # Verify parent task was moved
    parent_task = TodoItem.query.get(3)
    assert parent_task.list_id == 2

    # Verify children were moved with parent
    child_task_1 = TodoItem.query.get(4)
    child_task_2 = TodoItem.query.get(5)
    assert child_task_1.list_id == 2
    assert child_task_2.list_id == 2
    assert child_task_1.parent_id == 3
    assert child_task_2.parent_id == 3


def test_move_task_unauthorized(setup_lists_and_tasks, client):
    """Test that unauthorized users cannot move tasks"""
    # Logout current user
    client.get("/logout")

    # Try to move task without authentication
    response = client.post(
        "/item/1/move",
        data={"list_id": 2},
        follow_redirects=True,
    )
    assert b"Please log in" in response.data

    # Verify task wasn't moved
    task = TodoItem.query.get(1)
    assert task.list_id == 1


def test_move_task_to_nonexistent_list(setup_lists_and_tasks):
    """Test moving a task to a nonexistent list"""
    client = setup_lists_and_tasks

    response = client.post(
        "/item/1/move",
        data={"list_id": 999},
        follow_redirects=True,
    )
    assert response.status_code in [404, 302]

    # Verify task wasn't moved
    task = TodoItem.query.get(1)
    assert task.list_id == 1
