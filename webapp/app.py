from flask import jsonify

from webapp import create_app
from webapp.cache import Cache
from webapp.parser_task import ParserTask
from webapp.site_repository import SiteRepository, SiteRepositoryError
from webapp.sso import init_sso, login_required
from os import environ

app = create_app()

# Initialize SSO
init_sso(app)

#Initialize cache if available
try:
    cache = Cache(app)
except ConnectionError:
    cache = None
cache = None

# Start parser task
parser_task = ParserTask(app, cache=cache)

@app.route("/get-tree/<string:uri>", methods=["GET"])
@app.route("/get-tree/<string:uri>/<string:branch>", methods=["GET"])
@login_required
def region(uri, branch="main"):
    try:
        site_repository = SiteRepository(uri, branch, app=app, cache=cache)
    except SiteRepositoryError as e:
        return jsonify({"error": str(e)})

    tree = site_repository.get_tree()

    response = jsonify({"name": uri, "templates": tree})

    DEVELOPMENT_MODE = environ.get("DEVEL", True)
    if DEVELOPMENT_MODE:
        response.headers.add("Access-Control-Allow-Origin", "*")

    return response

