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
    """Create and authenticate a test user"""
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
def test_list(authenticated_client):
    """Create a test list for the authenticated user"""
    authenticated_client.post("/list/create", data={"title": "Test List"})
    return TodoList.query.filter_by(title="Test List").first()


def test_create_item_hierarchy(authenticated_client, test_list):
    """Test creating items at all three levels of hierarchy"""
    # Create top-level item
    response = authenticated_client.post(
        "/item/create", data={"list_id": test_list.id, "title": "Level 1 Item"}
    )
    assert response.status_code == 302
    level1_item = TodoItem.query.filter_by(title="Level 1 Item").first()
    assert level1_item is not None
    assert level1_item.parent_id is None
    assert level1_item.get_level() == 0

    # Create sub-item (level 2)
    response = authenticated_client.post(
        "/item/create",
        data={
            "list_id": test_list.id,
            "parent_id": level1_item.id,
            "title": "Level 2 Item",
        },
    )
    assert response.status_code == 302
    level2_item = TodoItem.query.filter_by(title="Level 2 Item").first()
    assert level2_item is not None
    assert level2_item.parent_id == level1_item.id
    assert level2_item.get_level() == 1

    # Create sub-sub-item (level 3)
    response = authenticated_client.post(
        "/item/create",
        data={
            "list_id": test_list.id,
            "parent_id": level2_item.id,
            "title": "Level 3 Item",
        },
    )
    assert response.status_code == 302
    level3_item = TodoItem.query.filter_by(title="Level 3 Item").first()
    assert level3_item is not None
    assert level3_item.parent_id == level2_item.id
    assert level3_item.get_level() == 2


def test_maximum_nesting_level(authenticated_client, test_list):
    """Test that items cannot be nested beyond 3 levels"""
    # Create items at all levels
    response1 = authenticated_client.post(
        "/item/create", data={"list_id": test_list.id, "title": "Level 1"}
    )
    level1_item = TodoItem.query.filter_by(title="Level 1").first()

    response2 = authenticated_client.post(
        "/item/create",
        data={"list_id": test_list.id, "parent_id": level1_item.id, "title": "Level 2"},
    )
    level2_item = TodoItem.query.filter_by(title="Level 2").first()

    response3 = authenticated_client.post(
        "/item/create",
        data={"list_id": test_list.id, "parent_id": level2_item.id, "title": "Level 3"},
    )
    level3_item = TodoItem.query.filter_by(title="Level 3").first()

    # Attempt to create a fourth level (should fail)
    response4 = authenticated_client.post(
        "/item/create",
        data={"list_id": test_list.id, "parent_id": level3_item.id, "title": "Level 4"},
    )
    level4_item = TodoItem.query.filter_by(title="Level 4").first()
    assert level4_item is None  # Should not be created


def test_edit_items_at_all_levels(authenticated_client, test_list):
    """Test editing items at each level of the hierarchy"""
    # Create items at all levels
    authenticated_client.post(
        "/item/create",
        data={"list_id": test_list.id, "title": "Level 1", "parent_id": None},
    )
    level1_item = TodoItem.query.filter_by(title="Level 1").first()

    authenticated_client.post(
        "/item/create",
        data={"list_id": test_list.id, "parent_id": level1_item.id, "title": "Level 2"},
    )
    level2_item = TodoItem.query.filter_by(title="Level 2").first()

    authenticated_client.post(
        "/item/create",
        data={"list_id": test_list.id, "parent_id": level2_item.id, "title": "Level 3"},
    )
    level3_item = TodoItem.query.filter_by(title="Level 3").first()

    # Edit each level
    items_to_edit = [
        (level1_item, "Level 1 Edited"),
        (level2_item, "Level 2 Edited"),
        (level3_item, "Level 3 Edited"),
    ]

    for item, new_title in items_to_edit:
        response = authenticated_client.post(
            f"/item/{item.id}/edit",
            data={
                "title": new_title,
                "list_id": test_list.id,  # Add list_id to the request
            },
        )
        assert response.status_code in [200, 302]
        db.session.refresh(item)  # Refresh the item from the database
        assert item.title == new_title


def test_delete_items_at_all_levels(authenticated_client, test_list):
    """Test deleting items at each level and verifying cascading deletes"""
    # Create full hierarchy
    authenticated_client.post(
        "/item/create",
        data={"list_id": test_list.id, "title": "Level 1", "parent_id": None},
    )
    level1_item = TodoItem.query.filter_by(title="Level 1").first()

    authenticated_client.post(
        "/item/create",
        data={"list_id": test_list.id, "parent_id": level1_item.id, "title": "Level 2"},
    )
    level2_item = TodoItem.query.filter_by(title="Level 2").first()

    authenticated_client.post(
        "/item/create",
        data={"list_id": test_list.id, "parent_id": level2_item.id, "title": "Level 3"},
    )
    level3_item = TodoItem.query.filter_by(title="Level 3").first()

    # Verify initial setup
    assert level1_item is not None
    assert level2_item is not None
    assert level3_item is not None

    # Delete level 1 item and verify cascading delete
    response = authenticated_client.post(
        f"/item/{level1_item.id}/delete", data={"list_id": test_list.id}
    )
    assert response.status_code == 302

    # Verify all items are deleted
    db.session.expire_all()  # Refresh the session to ensure we get current state
    assert TodoItem.query.get(level1_item.id) is None
    assert TodoItem.query.get(level2_item.id) is None
    assert TodoItem.query.get(level3_item.id) is None


def test_move_items_between_lists(authenticated_client):
    """Test moving items between different lists"""
    # Create two lists
    authenticated_client.post("/list/create", data={"title": "List 1"})
    authenticated_client.post("/list/create", data={"title": "List 2"})
    list1 = TodoList.query.filter_by(title="List 1").first()
    list2 = TodoList.query.filter_by(title="List 2").first()

    # Create hierarchical items in first list
    authenticated_client.post(
        "/item/create", data={"list_id": list1.id, "title": "Parent Item"}
    )
    parent_item = TodoItem.query.filter_by(title="Parent Item").first()

    authenticated_client.post(
        "/item/create",
        data={"list_id": list1.id, "parent_id": parent_item.id, "title": "Child Item"},
    )

    # Move parent item (and its child) to second list
    response = authenticated_client.post(
        f"/item/{parent_item.id}/move", data={"list_id": list2.id}
    )
    assert response.status_code == 302

    # Verify items moved correctly
    moved_parent = TodoItem.query.filter_by(title="Parent Item").first()
    moved_child = TodoItem.query.filter_by(title="Child Item").first()
    assert moved_parent.list_id == list2.id
    assert moved_child.list_id == list2.id
    assert moved_child.parent_id == moved_parent.id


def test_move_maintains_hierarchy(authenticated_client):
    """Test that moving items maintains their hierarchical relationships"""
    # Create two lists
    authenticated_client.post("/list/create", data={"title": "Source List"})
    authenticated_client.post("/list/create", data={"title": "Target List"})
    source_list = TodoList.query.filter_by(title="Source List").first()
    target_list = TodoList.query.filter_by(title="Target List").first()

    # Create a three-level hierarchy
    authenticated_client.post(
        "/item/create", data={"list_id": source_list.id, "title": "Top Item"}
    )
    top_item = TodoItem.query.filter_by(title="Top Item").first()

    authenticated_client.post(
        "/item/create",
        data={
            "list_id": source_list.id,
            "parent_id": top_item.id,
            "title": "Middle Item",
        },
    )
    middle_item = TodoItem.query.filter_by(title="Middle Item").first()

    authenticated_client.post(
        "/item/create",
        data={
            "list_id": source_list.id,
            "parent_id": middle_item.id,
            "title": "Bottom Item",
        },
    )

    # Move the top item to the target list
    response = authenticated_client.post(
        f"/item/{top_item.id}/move", data={"list_id": target_list.id}
    )
    assert response.status_code == 302

    # Verify the entire hierarchy moved and maintained relationships
    moved_top = TodoItem.query.filter_by(title="Top Item").first()
    moved_middle = TodoItem.query.filter_by(title="Middle Item").first()
    moved_bottom = TodoItem.query.filter_by(title="Bottom Item").first()

    assert all(
        item.list_id == target_list.id
        for item in [moved_top, moved_middle, moved_bottom]
    )
    assert moved_middle.parent_id == moved_top.id
    assert moved_bottom.parent_id == moved_middle.id


def test_toggle_item_completion(authenticated_client, test_list):
    """Test marking items as complete and verifying cascade to children"""
    # Create parent with children
    authenticated_client.post(
        "/item/create", data={"list_id": test_list.id, "title": "Parent Task"}
    )
    parent = TodoItem.query.filter_by(title="Parent Task").first()

    authenticated_client.post(
        "/item/create",
        data={"list_id": test_list.id, "parent_id": parent.id, "title": "Child Task"},
    )
    child = TodoItem.query.filter_by(title="Child Task").first()

    # Toggle parent completion
    response = authenticated_client.post(f"/item/{parent.id}/toggle")
    assert response.status_code == 302

    # Verify both parent and child are marked complete
    db.session.refresh(parent)
    db.session.refresh(child)
    assert parent.completed is True
    assert child.completed is True


def test_toggle_item_expansion(authenticated_client, test_list):
    """Test expanding/collapsing items"""
    # Create item
    authenticated_client.post(
        "/item/create", data={"list_id": test_list.id, "title": "Expandable Task"}
    )
    item = TodoItem.query.filter_by(title="Expandable Task").first()

    # Toggle expansion
    response = authenticated_client.post(f"/item/{item.id}/expand")
    assert response.status_code == 302

    db.session.refresh(item)
    assert item.is_expanded is False

    # Toggle back
    response = authenticated_client.post(f"/item/{item.id}/expand")
    db.session.refresh(item)
    assert item.is_expanded is True


def test_show_hide_completed_items(authenticated_client, test_list):
    """Test toggling visibility of completed items in a list"""
    # Create and complete an item
    authenticated_client.post(
        "/item/create", data={"list_id": test_list.id, "title": "Completed Task"}
    )
    item = TodoItem.query.filter_by(title="Completed Task").first()
    authenticated_client.post(f"/item/{item.id}/toggle")

    # Toggle completed items visibility
    response = authenticated_client.post(f"/list/{test_list.id}/toggle-completed")
    assert response.status_code == 302

    # Verify list preference was updated
    db.session.refresh(test_list)
    assert test_list.show_completed is False

    # Toggle back
    authenticated_client.post(f"/list/{test_list.id}/toggle-completed")
    db.session.refresh(test_list)
    assert test_list.show_completed is True
