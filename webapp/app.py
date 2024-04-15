from flask import jsonify
from werkzeug.exceptions import NotFound

from webapp import create_app
from webapp.cache import Cache
from webapp.parser_task import ParserTask
from webapp.site_repository import SiteRepository, SiteRepositoryError

app = create_app()


@app.errorhandler(NotFound)
def handle_bad_request(e):
    return "Site repository not found!", 404


# Initialize cache if available
try:
    cache = Cache(app)
except ConnectionError:
    cache = None

# Start parser task
parser_task = ParserTask(app)


@app.route("/get-tree/<string:uri>", methods=["GET"])
@app.route("/get-tree/<string:uri>/<string:branch>", methods=["GET"])
def region(uri, branch="main"):
    try:
        site_repository = SiteRepository(uri, branch, app=app, cache=cache)
    except SiteRepositoryError as e:
        return handle_bad_request(e)

    tree = site_repository.get_tree()

    return jsonify({"name": uri, "templates": tree})
