"""Fabrique Flask — calquée sur l'app factory du monolith."""

from flask import Flask

from server.etl.api import imports_bp
from server.logging_setup import configure_logging


def create_app() -> Flask:
    """Crée et configure l'application Flask."""
    configure_logging()
    app = Flask(__name__)
    app.register_blueprint(imports_bp)
    return app
