import requests
from os import environ
from datetime import datetime
from flask import jsonify, render_template, request
from flask_pydantic import validate
from sqlalchemy.exc import SQLAlchemyError
from webapp.tasks import LOCKS
from webapp.sso import login_required
from webapp.site_repository import SiteRepository
from webapp.schemas import ChangesRequestModel, CreatePageModel
from webapp.models import (
    Reviewer,
    Webpage,
    JiraTask,
    db,
    get_or_create,
    WebpageStatus,
)
from webapp import create_app
from webapp.helper import (
    create_jira_task,
    get_or_create_user_id,
    get_project_id,
    get_webpage_id,
    create_copy_doc,
)

app = create_app()


@app.route("/api/get-tree/<string:uri>/<string:branch>", methods=["GET"])
@app.route(
    "/api/get-tree/<string:uri>/<string:branch>/<string:no_cache>",
    methods=["GET"],
)
@login_required
def get_tree(uri: str, branch: str = "main", no_cache: bool = False):
    site_repository = SiteRepository(uri, app, branch=branch, task_locks=LOCKS)
    # Getting the site tree here ensures that both the cache and db are updated
    tree = site_repository.get_tree_sync(no_cache)

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


@app.route("/api/get-users/<username>", methods=["GET"])
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


@app.route("/api/set-reviewers", methods=["POST"])
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


@app.route("/api/set-owner", methods=["POST"])
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


@app.route("/api/request-changes", methods=["POST"])
@login_required
@validate()
def request_changes(body: ChangesRequestModel):

    # Make a request to JIRA to create a task
    try:
        create_jira_task(app, body.model_dump())
    except Exception as e:
        return jsonify(str(e)), 500

    return jsonify({"message": "Task created successfully"}), 201


@app.route("/api/get-jira-tasks/<webpage_id>", methods=["GET"])
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


@app.route("/api/remove_webpage", methods=["POST"])
@validate()
@login_required
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
    webpage_id = body.webpage_id

    webpage = Webpage.query.filter(Webpage.id == webpage_id).one_or_none()
    if webpage is None:
        return jsonify({"error": "webpage not found"}), 404
    if webpage.status == WebpageStatus.NEW:
        try:
            jira_tasks = JiraTask.query.filter_by(webpage_id=webpage_id).all()
            if jira_tasks:
                for task in jira_tasks:
                    status_change = app.config["JIRA"].change_issue_status(
                        issue_id=task.jira_id,
                        transition_id=JiraStatusTransitionCodes.REJECTED.value,
                    )
                    if status_change["status_code"] != 204:
                        return (
                            jsonify(
                                {
                                    "error": f"failed to change status of Jira task {task.jira_id}"
                                }
                            ),
                            500,
                        )
                    JiraTask.query.filter_by(id=task.id).delete()

            Reviewer.query.filter_by(webpage_id=webpage_id).delete()
            db.session.delete(webpage)
            db.session.commit()

        except Exception as e:
            # Rollback if there's any error
            db.session.rollback()
            app.logger.info(e, "Error deleting webpage from the database")
            return jsonify({"error": f"unable to delete the webpage"}), 500

        return (
            jsonify(
                {
                    "message": f"request for removal of webpage is processed successfully"
                }
            ),
            201,
        )

    if webpage.status == WebpageStatus.AVAILABLE:
        if not (
            body.reporter_id
            and User.query.filter_by(id=body.reporter_id).one_or_none()
        ):
            return (
                jsonify(
                    {
                        "error": "provided parameters are incorrect of incomplete"
                    }
                ),
                400,
            )
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
            {
                "message": f"request for removal of {webpage.name} processed successfully"
            }
        ),
        201,
    )


@app.route("/api/create-page", methods=["POST"])
@login_required
@validate()
def create_page(body: CreatePageModel):
    data = body.model_dump()

    owner_id = get_or_create_user_id(data["owner"])

    # Create new webpage
    project_id = get_project_id(data["project"])
    new_webpage = get_or_create(
        db.session,
        Webpage,
        True,
        project_id=project_id,
        name=data["name"],
        url=data["name"],
        parent_id=get_webpage_id(data["parent"], project_id),
        owner_id=owner_id,
        status=WebpageStatus.NEW,
    )

    # Create new reviewer rows
    for reviewer in data["reviewers"]:
        reviewer_id = get_or_create_user_id(reviewer)
        get_or_create(
            db.session,
            Reviewer,
            user_id=reviewer_id,
            webpage_id=new_webpage[0].id,
        )

    copy_doc = data["copy_doc"]
    if not copy_doc:
        copy_doc = create_copy_doc(app, new_webpage[0])
        new_webpage[0].copy_doc_link = copy_doc
        db.session.commit()

    return jsonify({"copy_doc": copy_doc}), 201


# Client-side routes
@app.route("/")
@app.route("/new-webpage")
@login_required
def index():
    return render_template("index.html")


@app.route("/webpage/<path:path>")
@login_required
def webpage(path):
    return render_template("index.html")
