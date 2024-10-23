"""Configuration settings for the Medieval Todo List application."""

import os
from typing import Optional, Dict, Any


class Config:
    """Base configuration class for the application."""

    SECRET_KEY: str = os.environ.get("SECRET_KEY") or "medieval-default-secret-key"
    SQLALCHEMY_DATABASE_URI: str = (
        os.environ.get("DATABASE_URL") or "sqlite:///medieval_todos.db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS: bool = False


class TestConfig(Config):
    """Configuration for testing environment."""

    TESTING: bool = True
    SQLALCHEMY_DATABASE_URI: str = "sqlite:///:memory:"
    WTF_CSRF_ENABLED: bool = False


class DevelopmentConfig(Config):
    """Configuration for development environment."""

    DEBUG: bool = True


class ProductionConfig(Config):
    """Configuration for production environment."""

    DEBUG: bool = False


# Configuration dictionary for easy access
config: Dict[str, Any] = {
    "development": DevelopmentConfig,
    "testing": TestConfig,
    "production": ProductionConfig,
    "default": DevelopmentConfig,
}
