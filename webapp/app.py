from flask import jsonify

from webapp import create_app
from webapp.cache import Cache
from webapp.parser_task import ParserTask
from webapp.site_repository import SiteRepository, SiteRepositoryError
from os import environ, getcwd
import sys
import os
app = create_app()


#Initialize cache if available
# try:
#     cache = Cache(app)
# except ConnectionError:
#     cache = None
cache = None

# Start parser task
parser_task = ParserTask(app, cache=cache)


@app.route("/get-tree/<string:uri>", methods=["GET"])
@app.route("/get-tree/<string:uri>/<string:branch>", methods=["GET"])
def region(uri, branch="main"):
    print("Started logging     \n")
    try:
        os.chdir("/srv/")
        print("f2 ",getcwd())
        sys.stdout.flush()
        site_repository = SiteRepository(uri, branch, app=app, cache=None)
    except SiteRepositoryError as e:
        return jsonify({"error": str(e)})

    tree = site_repository.get_tree()
    print("f3 ",getcwd())
    sys.stdout.flush()
    response = jsonify({"name": uri, "templates": tree})

    DEVELOPMENT_MODE = environ.get("DEVEL", True)
    if DEVELOPMENT_MODE:
        response.headers.add("Access-Control-Allow-Origin", "*")

    return response

