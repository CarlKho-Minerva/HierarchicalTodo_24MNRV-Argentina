"""Initialize the Flask application and its extensions."""

from typing import Optional, Type
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager
from config import Config

# Initialize extensions
db = SQLAlchemy()
login_manager = LoginManager()
login_manager.login_view = "auth.login"


def create_app(config_class: Type[Config] = Config) -> Flask:
    """
    Create and configure the Flask application.

    Args:
        config_class: Configuration class to use for the application.
            Defaults to base Config class.

    Returns:
        Flask: Configured Flask application instance.
    """
    app = Flask(__name__)
    app.config.from_object(config_class)

    # Initialize extensions with app
    db.init_app(app)
    login_manager.init_app(app)

    # Register blueprints
    from app.routes import auth, todos

    app.register_blueprint(auth.bp)
    app.register_blueprint(todos.bp)

    # Create database tables
    with app.app_context():
        db.create_all()

    return app
