"""Todo management routes for the Medieval Todo List application."""

from flask import (
    Blueprint,
    render_template,
    request,
    jsonify,
    flash,
    redirect,
    url_for,
    request,
)
from flask_login import login_required, current_user
from typing import Union, Dict, Any
from app.models.todo import TodoList, TodoItem
from app import db

bp = Blueprint("todos", __name__)


@bp.route("/")
@login_required
def index() -> str:
    """
    Display the user's todo lists and items.

    Returns:
        str: Rendered todo list template
    """
    lists = TodoList.query.filter_by(user_id=current_user.id).all()
    return render_template("todos.html", lists=lists)


@bp.route("/list/create", methods=["POST"])
@login_required
def create_list() -> Union[Dict[str, Any], redirect]:
    """Create a new todo list.

    Returns:
        Union[Dict[str, Any], redirect]: JSON response or redirect
    """
    title = request.form.get("title")
    if not title:
        flash("Title is required.", "error")
        return redirect(url_for("todos.index"))

    todo_list = TodoList(title=title, user_id=current_user.id)
    db.session.add(todo_list)
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True, "id": todo_list.id, "title": todo_list.title})

    flash("List created successfully!", "success")
    return redirect(url_for("todos.index"))


@bp.route("/item/create", methods=["POST"])
@login_required
def create_item() -> Union[Dict[str, Any], redirect]:
    """Create a new todo item."""
    list_id = request.form.get("list_id", type=int)
    parent_id = request.form.get("parent_id", type=int)
    title = request.form.get("title")

    if not all([list_id, title]):
        flash("List ID and title are required.", "error")
        return redirect(url_for("todos.index"))

    todo_list = TodoList.query.get_or_404(list_id)
    if todo_list.user_id != current_user.id:
        flash("Unauthorized action.", "error")
        return redirect(url_for("todos.index"))

    if parent_id:
        parent = TodoItem.query.get_or_404(parent_id)
        if not parent.can_have_children():
            flash("Maximum nesting level reached.", "error")
            return redirect(url_for("todos.index"))

    # Create the item with explicit defaults
    item = TodoItem(
        title=title,
        list_id=list_id,
        parent_id=parent_id,
        completed=False,
        is_expanded=True,
    )
    db.session.add(item)
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(
            {
                "success": True,
                "id": item.id,
                "title": item.title,
                "parent_id": item.parent_id,
            }
        )

    flash("Item created successfully!", "success")
    return redirect(url_for("todos.index"))


@bp.route("/list/<int:list_id>/delete", methods=["POST"])
@login_required
def delete_list(list_id: int) -> Union[Dict[str, Any], redirect]:
    """
    Delete a todo list and all its items.

    Args:
        list_id: ID of the list to delete

    Returns:
        Union[Dict[str, Any], redirect]: JSON response for API calls,
        redirect for form submissions
    """
    todo_list = TodoList.query.get_or_404(list_id)

    if todo_list.user_id != current_user.id:
        flash("Unauthorized action.", "error")
        return redirect(url_for("todos.index"))

    try:
        # First, recursively delete all items in the list
        items_to_delete = []

        def get_items_recursively(items):
            for item in items:
                items_to_delete.append(item)
                get_items_recursively(item.children)

        get_items_recursively(todo_list.items)

        # Delete all items in reverse order (children first)
        for item in reversed(items_to_delete):
            db.session.delete(item)

        # Then delete the list itself
        db.session.delete(todo_list)
        db.session.commit()

        if request.headers.get("X-Requested-With") == "XMLHttpRequest":
            return jsonify({"success": True})

        flash("List deleted successfully!", "success")
    except Exception as e:
        db.session.rollback()
        flash("Error deleting list.", "error")

    return redirect(url_for("todos.index"))


@bp.route("/list/<int:list_id>/edit", methods=["POST"])
@login_required
def edit_list(list_id: int) -> Union[Dict[str, Any], redirect]:
    """
    Edit the name of a todo list.

    Args:
        list_id: ID of the list to edit

    Returns:
        Union[Dict[str, Any], redirect]: JSON response for API calls,
        redirect for form submissions
    """
    new_title = request.form.get("title")
    if not new_title:
        flash("Title is required.", "error")
        return redirect(url_for("todos.index"))

    todo_list = TodoList.query.get_or_404(list_id)
    if todo_list.user_id != current_user.id:
        flash("Unauthorized action.", "error")
        return redirect(url_for("todos.index"))

    todo_list.update_title(new_title)
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})

    flash("List name updated successfully!", "success")
    return redirect(url_for("todos.index"))


@bp.route("/item/<int:item_id>/toggle", methods=["POST"])
@login_required
def toggle_item(item_id):
    """Toggle completion status of an item."""
    item = TodoItem.query.get_or_404(item_id)

    # Use the toggle_completed method that handles children
    item.toggle_completed()
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({
            "success": True,
            "completed": item.completed
        })

    flash("Item status updated.", "success")
    return redirect(url_for("todos.index"))

# Add a new route to fetch list items separately
@bp.route("/list/<int:list_id>/items")
@login_required
def get_list_items(list_id):
    """Get items for a specific list (used for AJAX updates)."""
    todo_list = TodoList.query.get_or_404(list_id)
    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return render_template("_items_container.html", list=todo_list)
    return redirect(url_for("todos.index"))


@bp.route("/item/<int:item_id>/expand", methods=["POST"])
@login_required
def toggle_expand(item_id: int) -> Union[Dict[str, Any], redirect]:
    """
    Toggle the expanded status of a todo item.

    Args:
        item_id: ID of the item to toggle

    Returns:
        Union[Dict[str, Any], redirect]: JSON response for API calls,
        redirect for form submissions
    """
    item = TodoItem.query.get_or_404(item_id)

    item.toggle_expanded()
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"expanded": item.is_expanded})

    return redirect(url_for("todos.index"))


@bp.route("/item/<int:item_id>/move", methods=["POST"])
@login_required
def move_item(item_id: int) -> Union[Dict[str, Any], redirect]:
    """
    Move a todo item to a different list.

    Args:
        item_id: ID of the item to move

    Returns:
        Union[Dict[str, Any], redirect]: JSON response for API calls,
        redirect for form submissions
    """
    item = TodoItem.query.get_or_404(item_id)
    todo_list = TodoList.query.get_or_404(item.list_id)

    if todo_list.user_id != current_user.id:
        flash("Unauthorized action.", "error")
        return redirect(url_for("todos.index"))

    new_list_id = request.form.get("list_id", type=int)
    if not new_list_id:
        flash("New list ID is required.", "error")
        return redirect(url_for("todos.index"))

    new_list = TodoList.query.get_or_404(new_list_id)
    if new_list.user_id != current_user.id:
        flash("Unauthorized action.", "error")
        return redirect(url_for("todos.index"))

    # Move item to new list as a top-level item
    item.move_to_list(new_list_id, as_top_level=True)
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})

    flash("Item moved successfully!", "success")
    return redirect(url_for("todos.index"))


@bp.route("/item/<int:item_id>/edit", methods=["POST"])
@login_required
def edit_item(item_id: int) -> Union[Dict[str, Any], redirect]:
    """
    Edit the name of a todo item.

    Args:
        item_id: ID of the item to edit

    Returns:
        Union[Dict[str, Any], redirect]: JSON response for API calls,
        redirect for form submissions
    """
    item = TodoItem.query.get_or_404(item_id)
    todo_list = TodoList.query.get_or_404(item.list_id)

    if todo_list.user_id != current_user.id:
        flash("Unauthorized action.", "error")
        return redirect(url_for("todos.index"))

    new_title = request.form.get("title")
    if not new_title:
        flash("Title is required.", "error")
        return redirect(url_for("todos.index"))

    item.update_title(new_title)
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})

    flash("Item name updated successfully!", "success")
    return redirect(url_for("todos.index"))


@bp.route("/item/<int:item_id>/delete", methods=["POST"])
@login_required
def delete_item(item_id: int) -> Union[Dict[str, Any], redirect]:
    """
    Delete a todo item.

    Args:
        item_id: ID of the item to delete

    Returns:
        Union[Dict[str, Any], redirect]: JSON response for API calls,
        redirect for form submissions
    """
    item = TodoItem.query.get_or_404(item_id)
    todo_list = TodoList.query.get_or_404(item.list_id)

    if todo_list.user_id != current_user.id:
        flash("Unauthorized action.", "error")
        return redirect(url_for("todos.index"))

    db.session.delete(item)
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})

    flash("Item deleted successfully!", "success")
    return redirect(url_for("todos.index"))


@bp.route(
    "/list/<int:list_id>/toggle-completed", methods=["POST"]
)  # Changed from toggle_completed to toggle-completed
@login_required
def toggle_completed_view(list_id):
    """Toggle visibility of completed items in a list."""
    todo_list = TodoList.query.filter_by(
        id=list_id, user_id=current_user.id
    ).first_or_404()

    # Toggle the show_completed flag
    todo_list.show_completed = not todo_list.show_completed
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(
            {
                "success": True,
                "show_completed": todo_list.show_completed,
                "message": "Completed items are now "
                + ("visible" if todo_list.show_completed else "hidden"),
            }
        )

    flash(
        "Completed items are now "
        + ("visible" if todo_list.show_completed else "hidden"),
        "info",
    )
    return redirect(url_for("todos.index"))


@bp.route("/item/move-position", methods=["POST"])
@login_required
def move_item_position():
    data = request.json
    item_id = data.get("item_id")
    target_id = data.get("target_id")

    if not item_id or not target_id:
        return jsonify({"success": False}), 400

    try:
        item = TodoItem.query.get_or_404(item_id)
        target = TodoItem.query.get_or_404(target_id)

        # Ensure user owns both items
        if (
            item.list.user_id != current_user.id
            or target.list.user_id != current_user.id
        ):
            return jsonify({"success": False}), 403

        # Update positions
        old_position = item.position
        new_position = target.position

        if old_position < new_position:
            # Moving down
            TodoItem.query.filter(
                TodoItem.list_id == item.list_id,
                TodoItem.position > old_position,
                TodoItem.position <= new_position,
            ).update({"position": TodoItem.position - 1})
        else:
            # Moving up
            TodoItem.query.filter(
                TodoItem.list_id == item.list_id,
                TodoItem.position >= new_position,
                TodoItem.position < old_position,
            ).update({"position": TodoItem.position + 1})

        item.position = new_position
        db.session.commit()

        return jsonify({"success": True})

    except Exception as e:
        db.session.rollback()
        return jsonify({"success": False}), 500


@property
def visible_items(self):
    """Return visible top-level items based on show_completed setting"""
    items = self.items.filter_by(parent_id=None)
    if not self.show_completed:
        items = items.filter_by(completed=False)
    return items.order_by(TodoItem.created_at.desc()).all()
