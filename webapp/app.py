from os import environ

from flask import jsonify, render_template, request

from webapp import create_app
from webapp.site_repository import SiteRepository
from webapp.sso import login_required
from webapp.tasks import LOCKS

from webapp.models import get_or_create, db, Webpage, User, Reviewer

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
    first_name_query = """
    query($name: String!) {
        employees(filter: { firstName: $name }) {
            id
            name
            email
            team
            department
            jobTitle
        }
    }
    """

    last_name_query = """
    query($name: String!) {
        employees(filter: { surname: $name }) {
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

    formattedUsername = username.strip().title()

    # Currently directory-api only supports strict comparison of field values,
    # so we have to send two requests instead of one for first and last names
    first_name_response = requests.post(
        "https://directory.wpe.internal/graphql/", json={
            'query': first_name_query,
            'variables': {'name': formattedUsername},
        }, headers=headers, verify=False)

    last_name_response = requests.post(
        "https://directory.wpe.internal/graphql/", json={
            'query': last_name_query,
            'variables': {'name': formattedUsername},
        }, headers=headers, verify=False)

    if (first_name_response.status_code == 200 and
            last_name_response.status_code == 200):
        first_name_data = first_name_response.json().get('data', {}).get(
            'employees', [])
        last_name_data = last_name_response.json().get('data', {}).get(
            'employees', [])
        users = {emp['id']: emp for emp in first_name_data +
                 last_name_data}.values()
        return jsonify(list(users))
    else:
        return jsonify({"error": "Failed to fetch users"}), 500


@app.route('/set-reviewers', methods=['POST'])
@login_required
def set_reviewers():
    data = request.get_json()

    users = data.get("user_structs")
    webpage_id = data.get("webpage_id")

    user_ids = []
    for user in users:
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
        user_ids.append(user_exists.id)

    # Remove all existing reviewers for the webpage
    existing_reviewers = Reviewer.query.filter_by(webpage_id=webpage_id).all()
    for reviewer in existing_reviewers:
        db.session.delete(reviewer)
    db.session.commit()

    # Create new reviewer rows
    for user_id in user_ids:
        get_or_create(db.session,
                      Reviewer,
                      user_id=user_id,
                      webpage_id=webpage_id)

    return jsonify({"message": "Successfully set reviewers"}), 200
