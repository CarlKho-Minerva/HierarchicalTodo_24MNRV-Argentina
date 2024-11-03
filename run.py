"""Entry point for the Medieval Todo List application."""

import os
from app import create_app
from config import config

# Get configuration from environment or use default
config_name = os.environ.get("FLASK_CONFIG", "default")
app = create_app(config[config_name])

if __name__ == "__main__":
    # Run the application
    app.run(
        host=os.environ.get("FLASK_HOST", "127.0.0.1"),
        port=int(os.environ.get("FLASK_PORT", 5001)),
        debug=config[config_name].DEBUG,
    )
