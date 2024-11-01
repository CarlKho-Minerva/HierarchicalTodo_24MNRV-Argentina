"""Database migration script to add show_completed column"""

from app import create_app, db
from sqlalchemy import Column, Boolean

def upgrade():
    """Add show_completed column to todo_list table"""
    with create_app().app_context():
        db.engine.execute('ALTER TABLE todo_list ADD COLUMN show_completed BOOLEAN DEFAULT TRUE')

def downgrade():
    """Remove show_completed column from todo_list table"""
    with create_app().app_context():
        db.engine.execute('ALTER TABLE todo_list DROP COLUMN show_completed')

if __name__ == "__main__":
    upgrade()
