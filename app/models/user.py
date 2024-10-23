"""User model for the Medieval Todo List application."""

from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from typing import Optional
from app import db, login_manager


class User(UserMixin, db.Model):
    """
    User model representing application users.

    Attributes:
        id: Unique identifier for the user
        username: User's chosen username
        email: User's email address
        password_hash: Hashed version of user's password
        todo_lists: Relationship to user's todo lists
    """

    id: int = db.Column(db.Integer, primary_key=True)
    username: str = db.Column(db.String(64), unique=True, nullable=False)
    email: str = db.Column(db.String(120), unique=True, nullable=False)
    password_hash: str = db.Column(db.String(128))
    todo_lists = db.relationship("TodoList", backref="owner", lazy="dynamic")

    def set_password(self, password: str) -> None:
        """
        Set the user's password by generating a hash.

        Args:
            password: Plain text password to hash and store
        """
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """
        Verify if the provided password matches the stored hash.

        Args:
            password: Plain text password to verify

        Returns:
            bool: True if password matches, False otherwise
        """
        return check_password_hash(self.password_hash, password)


@login_manager.user_loader
def load_user(id: str) -> Optional[User]:
    """
    Load a user from the database using their ID.

    Args:
        id: User ID as a string

    Returns:
        Optional[User]: User object if found, None otherwise
    """
    return User.query.get(int(id))

