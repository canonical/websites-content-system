from flask import jsonify
from webapp import create_app
from webapp.redis import Redis
from webapp.site_repository import SiteRepository

app = create_app()

redis = Redis(app)


@app.route("/get-tree/<string:uri>/<string:branch>", methods=["GET"])
def region(uri, branch="main"):
    # We try to get the data from the cache
    # TODO: Make the folder name a url parameter
    # TODO: Redirect to the correct site, based on the reponame
    if not (data := redis.get(uri)):
        site_repository = SiteRepository(uri, branch, app=app)
        tree = site_repository.parse_templates()
    else:
        tree = dict(data)[branch]
        redis.set(uri, tree)
    return jsonify(tree)
