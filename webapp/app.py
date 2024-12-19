from os import environ
from flask import render_template

from webapp import create_app
from webapp.sso import login_required
from webapp.routes.tree import tree_blueprint
from webapp.routes.user import user_blueprint
from webapp.routes.jira import jira_blueprint

app = create_app()

# Server-side routes
app.register_blueprint(tree_blueprint)
app.register_blueprint(user_blueprint)
app.register_blueprint(jira_blueprint)


# Client-side routes
@app.route("/")
@app.route("/new-webpage")
@login_required
def index():
    return render_template(
        "index.html", is_dev=environ.get("FLASK_ENV") == "development"
    )


@app.route("/webpage/<path:path>")
@login_required
def webpage(path):
    return render_template(
        "index.html", is_dev=environ.get("FLASK_ENV") == "development"
    )
