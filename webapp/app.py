from flask import jsonify
from webapp import create_app
from webapp.redis import Redis
from webapp.site_repository import SiteRepository

app = create_app()

redis = Redis(app)


@app.route("/get-tree/<string:uri>", methods=["GET"])
@app.route("/get-tree/<string:uri>/<string:branch>", methods=["GET"])
def region(uri, branch="main"):
    # TODO: Make the folder name a url parameter
    # TODO: Redirect to the correct site, based on the reponame

    site_repository = SiteRepository(uri, branch, app=app)
    tree = site_repository.get_tree()

    return jsonify({"name": uri, "templates": tree})
