from os import environ

import requests
from flask import jsonify, render_template, request
from flask_pydantic import validate

from webapp import create_app
from webapp.helper import create_jira_task, get_or_create_user_id
from webapp.models import Reviewer, Webpage, db, get_or_create
from webapp.schemas import (
    ChangesRequestModel,
)
from webapp.site_repository import SiteRepository
from webapp.sso import login_required
from webapp.tasks import LOCKS

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


@app.route("/get-users/<username>", methods=["GET"])
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

    headers = {"Authorization": "token " + environ.get("DIRECTORY_API_TOKEN")}

    # Currently directory-api only supports strict comparison of field values,
    # so we have to send two requests instead of one for first and last names
    response = requests.post(
        "https://directory.wpe.internal/graphql/",
        json={
            "query": query,
            "variables": {"name": username.strip()},
        },
        headers=headers,
        verify=False,
    )

    if response.status_code == 200:
        users = response.json().get("data", {}).get("employees", [])
        return jsonify(list(users))
    else:
        return jsonify({"error": "Failed to fetch users"}), 500


@app.route("/set-reviewers", methods=["POST"])
@login_required
def set_reviewers():
    data = request.get_json()

    users = data.get("user_structs")
    webpage_id = data.get("webpage_id")

    user_ids = []
    for user in users:
        user_ids.append(get_or_create_user_id(user))

    # Remove all existing reviewers for the webpage
    existing_reviewers = Reviewer.query.filter_by(webpage_id=webpage_id).all()
    for reviewer in existing_reviewers:
        db.session.delete(reviewer)
    db.session.commit()

    # Create new reviewer rows
    for user_id in user_ids:
        get_or_create(
            db.session, Reviewer, user_id=user_id, webpage_id=webpage_id
        )

    return jsonify({"message": "Successfully set reviewers"}), 200


@app.route("/set-owner", methods=["POST"])
@login_required
def set_owner():
    data = request.get_json()

    user = data.get("user_struct")
    webpage_id = data.get("webpage_id")
    user_id = get_or_create_user_id(user)

    # Set owner_id of the webpage to the user_id
    webpage = Webpage.query.filter_by(id=webpage_id).first()
    if webpage:
        webpage.owner_id = user_id
        db.session.commit()

    return jsonify({"message": "Successfully set owner"}), 200


@app.route("/request-changes", methods=["POST"])
@login_required
@validate()
def request_changes(body: ChangesRequestModel):

    # Make a request to JIRA to create a task
    try:
        create_jira_task(app, body.model_dump())
    except Exception as e:
        return jsonify(e), 500

    return jsonify("Task created successfully"), 201
