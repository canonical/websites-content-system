from flask import Flask
from webapp.context import base_context


def create_app():
    app = Flask(
        __name__,
        template_folder="../templates",
        static_folder="../static"
    )
    app.config.from_pyfile("settings.py")
    app.context_processor(base_context)
    return app
