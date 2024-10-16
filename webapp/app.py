from os import environ

import requests
from datetime import datetime
from flask import jsonify, render_template, request
from flask_pydantic import validate
from sqlalchemy.exc import SQLAlchemyError

from webapp import create_app
from webapp.helper import create_jira_task, get_or_create_user_id
from webapp.models import (
    Reviewer,
    Webpage,
    JiraTask,
    db,
    get_or_create,
    WebpageStatus,
    User,
)
from webapp.schemas import (
    ChangesRequestModel,
    RemoveWebpageModel,
)
from webapp.site_repository import SiteRepository
from webapp.sso import login_required
from webapp.tasks import LOCKS
from webapp.jira import Jira
from webapp.enums import JiraStatusTransitionCodes


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
        get_or_create(db.session, Reviewer, user_id=user_id, webpage_id=webpage_id)

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
        task = create_jira_task(app, body.model_dump())
        task_url = f"https://docs.google.com/document/d/{task['id']}"
    except Exception as e:
        return jsonify(str(e)), 500

    return jsonify({"message": f"Task created successfully\n{task_url}"}), 201


@app.route("/get-jira-tasks/<webpage_id>", methods=["GET"])
def get_jira_tasks(webpage_id: int):
    jira_tasks = (
        JiraTask.query.filter_by(webpage_id=webpage_id)
        .order_by(JiraTask.created_at)
        .all()
    )
    if jira_tasks:
        tasks = []
        for task in jira_tasks:
            tasks.append(
                {
                    "id": task.id,
                    "jira_id": task.jira_id,
                    "status": task.status,
                    "webpage_id": task.webpage_id,
                    "user_id": task.user_id,
                    "created_at": task.created_at,
                }
            )
        return jsonify(tasks), 200
    else:
        return jsonify({"error": "Failed to fetch Jira tasks"}), 500


@app.route("/api/webpage", methods=["POST"])
@validate()
def remove_webpage(body: RemoveWebpageModel):
    """
    Remove a webpage based on its status.
    This function handles the removal of a webpage from the system.
    If the webpage is new and not in the codebase, it deletes the webpage and associated
    reviewer records from the database. If the webpage pre-exists, it creates a Jira task to remove
    the webpage from the code repository and updates the webpage status to "TO_DELETE".
    Args:
        body (RemoveWebpageModel): The model containing the details of the webpage to be removed.
    Returns:
        Response: A JSON response indicating the result of the operation.
            - If the webpage is not found, returns a 404 error with a message.
            - If the webpage is successfully deleted or a task is created, returns a 201 status with a success message.
            - If there is an error during deletion, returns a 500 error with a message.
    """
    print(body.dict())
    webpage_id = body.webpage_id

    webpage = Webpage.query.filter(Webpage.id == webpage_id).one_or_none()
    print("webpage fetched ", webpage)
    if webpage is None:
        return jsonify({"error": "webpage not found"}), 404
    if webpage.status == WebpageStatus.NEW:
        try:
            jira_tasks = JiraTask.query.filter_by(webpage_id=webpage_id).all()
            if jira_tasks:
                for task in jira_tasks:
                    if app.config["JIRA"].change_issue_status(
                        issue_id=task.jira_id,
                        transition_id=JiraStatusTransitionCodes.REJECTED.value,
                    ):
                        JiraTask.query.filter_by(id=task.id).delete()

                db.session.commit()
            Reviewer.query.filter_by(webpage_id=webpage_id).delete()
            Webpage.query.filter_by(id=webpage_id).delete()
            db.session.commit()

        except SQLAlchemyError as e:
            # Rollback if there's any error
            db.session.rollback()
            print(f"Error deleting webpage: {str(e)}")  # log error
            return jsonify({"error": f"unable to delete the webpage"}), 500

        return (
            jsonify(
                {"message": f"request for removal of webpage is processed successfully"}
            ),
            201,
        )

    if webpage.status == WebpageStatus.AVAILABLE:
        if not (
            (
                body.due_date
                and datetime.strptime(body.due_date, "%Y-%m-%d") > datetime.now()
            )
            and (
                body.reporter_id
                and User.query.filter_by(id=body.reporter_id).one_or_none()
            )
        ):
            return (
                jsonify({"error": "provided parameters are incorrect of incomplete"}),
                400,
            )
        print("webpage status is available")
        task_details = {
            "webpage_id": webpage_id,
            "due_date": body.due_date,
            "reporter_id": body.reporter_id,
            "description": body.description,
            "type": None,
            "summary": f"Remove {webpage.name} webpage from code repository",
        }
        task = create_jira_task(app, task_details)
        Webpage.query.filter_by(id=webpage_id).update(
            {"status": WebpageStatus.TO_DELETE.value}
        )
        db.session.commit()

    return (
        jsonify(
            {"message": f"request for removal of {webpage.name} processed successfully"}
        ),
        201,
    )
