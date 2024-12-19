from os import environ

import requests
from flask import jsonify, request, Blueprint, current_app

from webapp.site_repository import SiteRepository
from webapp.sso import login_required
from webapp.tasks import LOCKS
from webapp.helper import get_or_create_user_id
from webapp.models import (
    Project,
    Reviewer,
    Webpage,
    db,
    get_or_create,
)

user_blueprint = Blueprint("user", __name__, url_prefix="/api")


@user_blueprint.route("/get-users/<username>", methods=["GET"])
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


@user_blueprint.route("/set-reviewers", methods=["POST"])
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

    webpage = Webpage.query.filter_by(id=webpage_id).first()
    project = Project.query.filter_by(id=webpage.project_id).first()
    site_repository = SiteRepository(
        project.name, current_app, task_locks=LOCKS
    )
    # clean the cache for a the new reviewers to appear in the tree
    site_repository.invalidate_cache()

    return jsonify({"message": "Successfully set reviewers"}), 200


@user_blueprint.route("/set-owner", methods=["POST"])
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

        project = Project.query.filter_by(id=webpage.project_id).first()
        site_repository = SiteRepository(
            project.name, current_app, task_locks=LOCKS
        )
        # clean the cache for a new owner to appear in the tree
        site_repository.invalidate_cache()

    return jsonify({"message": "Successfully set owner"}), 200
