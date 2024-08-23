from os import environ

from flask import jsonify, render_template

from webapp import create_app
from webapp.site_repository import SiteRepository
from webapp.sso import login_required
from webapp.tasks import LOCKS

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

    # Currently directory-api only supports strict comparison of field values,
    # so we have to send two requests instead of one for first and last names
    first_name_response = requests.post(
        "https://directory.wpe.internal/graphql/", json={
            'query': first_name_query,
            'variables': {'name': username},
        }, headers=headers, verify=False)

    last_name_response = requests.post(
        "https://directory.wpe.internal/graphql/", json={
            'query': last_name_query,
            'variables': {'name': username},
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
