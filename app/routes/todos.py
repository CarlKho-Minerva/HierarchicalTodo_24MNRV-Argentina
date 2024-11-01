"""Todo management routes for the Medieval Todo List application."""

from flask import Blueprint, render_template, request, jsonify, flash, redirect, url_for
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
    """
    Create a new todo list.

    Returns:
        Union[Dict[str, Any], redirect]: JSON response for API calls,
        redirect for form submissions
    """
    title = request.form.get("title")
    if not title:
        flash("Title is required.", "error")
        return redirect(url_for("todos.index"))

    todo_list = TodoList(title=title, user_id=current_user.id)
    db.session.add(todo_list)
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"id": todo_list.id, "title": todo_list.title})

    flash("List created successfully!", "success")
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

    db.session.delete(todo_list)
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})

    flash("List deleted successfully!", "success")
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


@bp.route("/item/create", methods=["POST"])
@login_required
def create_item() -> Union[Dict[str, Any], redirect]:
    """
    Create a new todo item.

    Returns:
        Union[Dict[str, Any], redirect]: JSON response for API calls,
        redirect for form submissions
    """
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

    item = TodoItem(title=title, list_id=list_id, parent_id=parent_id)
    db.session.add(item)
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify(
            {"id": item.id, "title": item.title, "parent_id": item.parent_id}
        )

    flash("Item created successfully!", "success")
    return redirect(url_for("todos.index"))


@bp.route("/item/<int:item_id>/toggle", methods=["POST"])
@login_required
def toggle_item(item_id):
    item = TodoItem.query.get(item_id)
    if item is None:
        flash("Item not found.", "error")
        return redirect(url_for("todos.index"))

    # Toggle the item's completion status
    item.completed = not item.completed
    db.session.commit()
    flash("Item status updated.", "success")
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

    if item.todo_list is None:
        flash("Todo list not found.", "error")
        return redirect(url_for("todos.index"))

    if item.todo_list.user_id != current_user.id:
        flash("You do not have permission to modify this item.", "error")
        return redirect(url_for("todos.index"))

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
    new_list_id = request.form.get("list_id", type=int)
    if not new_list_id:
        flash("New list ID is required.", "error")
        return redirect(url_for("todos.index"))

    item = TodoItem.query.get_or_404(item_id)
    new_list = TodoList.query.get_or_404(new_list_id)

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
    new_title = request.form.get("title")
    if not new_title:
        flash("Title is required.", "error")
        return redirect(url_for("todos.index"))

    item = TodoItem.query.get_or_404(item_id)
    if item.todo_list.user_id != current_user.id:
        flash("Unauthorized action.", "error")
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
    if item.todo_list.user_id != current_user.id:
        flash("Unauthorized action.", "error")
        return redirect(url_for("todos.index"))

    db.session.delete(item)
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"success": True})

    flash("Item deleted successfully!", "success")
    return redirect(url_for("todos.index"))


@bp.route("/list/<int:list_id>/toggle-completed", methods=["POST"])
@login_required
def toggle_completed_view(list_id: int) -> Union[Dict[str, Any], redirect]:
    """Toggle the visibility of completed items for a list."""
    todo_list = TodoList.query.get_or_404(list_id)

    if todo_list.user_id != current_user.id:
        flash("Unauthorized action.", "error")
        return redirect(url_for("todos.index"))

    todo_list.toggle_show_completed()
    db.session.commit()

    if request.headers.get("X-Requested-With") == "XMLHttpRequest":
        return jsonify({"show_completed": todo_list.show_completed})

    return redirect(url_for("todos.index"))
