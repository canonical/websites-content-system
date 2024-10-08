from flask import Flask

from webapp.cache import init_cache
from webapp.context import base_context
from webapp.gdrive import init_gdrive
from webapp.jira import init_jira
from webapp.models import init_db
from webapp.sso import init_sso
from webapp.tasks import init_tasks


def create_app():
    app = Flask(
        __name__, template_folder="../templates", static_folder="../static"
    )
    app.config.from_pyfile("settings.py")
    app.context_processor(base_context)

    # Initialize database
    init_db(app)

    # Initialize SSO
    init_sso(app)

    # Initialize cache
    init_cache(app)

    # Initialize tasks
    init_tasks(app)

    # Initialize JIRA
    init_jira(app)

    # Initialize gdrive
    init_gdrive(app)

    return app
