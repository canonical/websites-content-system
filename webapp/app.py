from os import environ

from flask import jsonify, render_template

from webapp import create_app
from webapp.sso import login_required
from webapp.tasks import get_tree_async

app = create_app()


@app.route("/get-tree/<string:uri>", methods=["GET"])
@app.route("/get-tree/<string:uri>/<string:branch>", methods=["GET"])
@login_required
def get_tree(uri, branch="main"):
    # Get tree if already generated, otherwise queue task
    # and return empty array.
    # This prevents concurrent cloning of the same repository.
    tree = get_tree_async(uri, branch, app)

    response = jsonify({"name": uri, "templates": tree})

    DEVELOPMENT_MODE = environ.get("DEVEL", True)
    if DEVELOPMENT_MODE:
        response.headers.add("Access-Control-Allow-Origin", "*")

    return response


@app.route("/", defaults={ "path": "" })
@app.route("/webpage/<path:path>")
@login_required
def index(path):
    return render_template("index.html")
