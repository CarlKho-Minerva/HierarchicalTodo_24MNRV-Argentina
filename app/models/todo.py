"""Todo models for the Medieval Todo List application."""

from datetime import datetime
from typing import Optional
from app import db
from sqlalchemy import Column, Boolean


class TodoList(db.Model):
    """
    TodoList model representing a collection of todo items.

    Attributes:
        id: Unique identifier for the list
        title: Title of the todo list
        created_at: Timestamp when list was created
        user_id: ID of the user who owns this list
        items: Relationship to top-level todo items in this list
    """

    id: int = Column(db.Integer, primary_key=True)
    title: str = Column(db.String(100), nullable=False)
    created_at: datetime = Column(db.DateTime, default=datetime.utcnow)
    user_id: int = Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    user_id: int = db.Column(db.Integer, db.ForeignKey("user.id"), nullable=False)
    items = db.relationship(
        "TodoItem",
        backref="todo_list",
        lazy="dynamic",
        primaryjoin="and_(TodoList.id==TodoItem.list_id, TodoItem.parent_id==None)",
    )
    show_completed: bool = Column(db.Boolean, default=True)

    def update_title(self, new_title: str) -> None:
        """
        Update the title of the todo list.

        Args:
            new_title: New title for the todo list
        """
        self.title = new_title

    def toggle_show_completed(self) -> None:
        """Toggle visibility of completed items."""
        self.show_completed = not self.show_completed

    @property
    def visible_items(self):
        """Return items based on show_completed preference."""
        base_query = self.items
        if not self.show_completed:
            base_query = base_query.filter_by(completed=False)
        return base_query


class TodoItem(db.Model):
    """
    TodoItem model representing a single todo item that can have sub-items.

    Attributes:
        id: Unique identifier for the item
        title: Title/description of the todo item
        created_at: Timestamp when item was created
        completed: Whether the item is completed
        list_id: ID of the parent todo list
        parent_id: ID of the parent todo item (if this is a sub-item)
        children: Relationship to child todo items
        is_expanded: Whether the item's children are shown in the UI
    """

    id: int = Column(db.Integer, primary_key=True)
    title: str = Column(db.String(200), nullable=False)
    created_at: datetime = Column(db.DateTime, default=datetime.utcnow)
    completed: bool = Column(db.Boolean, default=False)
    list_id: int = Column(db.Integer, db.ForeignKey("todo_list.id"), nullable=False)
    parent_id: Optional[int] = Column(db.Integer, db.ForeignKey("todo_item.id"))
    is_expanded: bool = Column(db.Boolean, default=True)

    # Self-referential relationship for hierarchical structure
    children = db.relationship(
        "TodoItem", backref=db.backref("parent", remote_side=[id]), lazy="dynamic"
    )

    def toggle_completed(self) -> None:
        """
        Toggle the completed status of this item and all its children.
        """
        self.completed = not self.completed
        for child in self.children:
            child.completed = self.completed

    def toggle_expanded(self) -> None:
        """
        Toggle the expanded status of this item.
        """
        self.is_expanded = not self.is_expanded

    def get_level(self) -> int:
        """
        Calculate how deep this item is in the hierarchy.

        Returns:
            int: The level of this item (0 for top-level, 1 for first sub-level, etc.)
        """
        level = 0
        current = self
        while current.parent_id is not None:
            level += 1
            current = current.parent
        return level

    def can_have_children(self) -> bool:
        """
        Check if this item can have children based on its current level.

        Returns:
            bool: True if the item can have children, False otherwise
        """
        return self.get_level() < 2  # Limit to 3 levels (0, 1, 2)

    def move_to_list(self, new_list_id: int, as_top_level: bool = False) -> None:
        """
        Move this item and all its children to a different list.

        Args:
            new_list_id: ID of the destination todo list
            as_top_level: Whether to move the item as a top-level item
        """
        self.list_id = new_list_id
        if as_top_level:
            self.parent_id = None
        for child in self.children:
            child.move_to_list(new_list_id)

    def update_title(self, new_title: str) -> None:
        """
        Update the title of the todo item.

        Args:
            new_title: New title for the todo item
        """
        self.title = new_title
