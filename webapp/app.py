from os import environ

from flask import jsonify, render_template, request

from webapp import create_app
from webapp.site_repository import SiteRepository
from webapp.sso import login_required
from webapp.tasks import LOCKS

from webapp.models import get_or_create, db, Webpage, User

import requests

app = create_app()


@app.route("/get-tree/<string:uri>", methods=["GET"])
@app.route("/get-tree/<string:uri>/<string:branch>", methods=["GET"])
@login_required
def get_tree(uri: str, branch="main"):
    site_repository = SiteRepository(uri, app, branch=branch, task_locks=LOCKS)
    # Getting the site tree here ensures that both the cache and db are updated
    tree = site_repository.get_tree_async()

    response = jsonify(
        {
            "name": uri,
            "templates": tree,
        }
    )

    DEVELOPMENT_MODE = environ.get("DEVEL", True)
    if DEVELOPMENT_MODE:
        response.headers.add("Access-Control-Allow-Origin", "*")

    return response


@app.route("/", defaults={"path": ""})
@app.route("/webpage/<path:path>")
@login_required
def index(path):
    return render_template("index.html")


@app.route('/get-users/<username>', methods=['GET'])
@login_required
def get_users(username: str):
    query = """
    query($name: String!) {
        employees(filter: { contains: { name: $name }}) {
            id
            name
            email
            team
            department
            jobTitle
        }
    }
    """

    headers = {
        "Authorization": "token " + environ.get("DIRECTORY_API_TOKEN")
    }

    # Currently directory-api only supports strict comparison of field values,
    # so we have to send two requests instead of one for first and last names
    response = requests.post(
        "https://directory.wpe.internal/graphql/", json={
            'query': query,
            'variables': {'name': username.strip()},
        }, headers=headers, verify=False)

    if (response.status_code == 200):
        users = response.json().get('data', {}).get(
            'employees', [])
        return jsonify(list(users))
    else:
        return jsonify({"error": "Failed to fetch users"}), 500


@app.route('/set-owner', methods=['POST'])
@login_required
def set_owner():
    data = request.get_json()

    user = data.get("user_struct")
    webpage_id = data.get("webpage_id")
    user_hrc_id = user.get("id")

    # If user does not exist, create a new user in the "users" table
    user_exists = User.query.filter_by(hrc_id=user_hrc_id).first()
    if not user_exists:
        user_exists, _ = get_or_create(db.session,
                                       User,
                                       name=user.get("name"),
                                       email=user.get("email"),
                                       team=user.get("team"),
                                       department=user.get("department"),
                                       job_title=user.get("jobTitle"),
                                       hrc_id=user_hrc_id)

    user_id = user_exists.id

    # Set owner_id of the webpage to the user_id
    webpage = Webpage.query.filter_by(id=webpage_id).first()
    if webpage:
        webpage.owner_id = user_id
        db.session.commit()

    return jsonify({"message": "Successfully set owner"}), 200
