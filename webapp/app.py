from webapp.tasks import LOCKS
from webapp.sso import login_required
from webapp.site_repository import SiteRepository
from webapp.schemas import (
    ChangesRequestModel,
)
from webapp.models import (
    Reviewer,
    Webpage,
    JiraTask,
    db,
    get_or_create,
    WebpageStatus
)
from os import environ

import requests
from flask import jsonify, render_template, request
from flask_pydantic import validate

from webapp import create_app
from webapp.helper import (
    create_jira_task,
    get_or_create_user_id,
    get_project_id,
    get_webpage_id,
    create_copy_doc
)

app = create_app()


@app.route("/api/get-tree/<string:uri>/<string:branch>", methods=["GET"])
@app.route(
    "/api/get-tree/<string:uri>/<string:branch>/<string:no_cache>",
    methods=["GET"]
)
@login_required
def get_tree(uri: str, branch: str = "main", no_cache: bool = False):
    site_repository = SiteRepository(
        uri,
        app,
        branch=branch,
        task_locks=LOCKS
    )
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
        get_or_create(db.session, Reviewer, user_id=user_id,
                      webpage_id=webpage_id)

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


@app.route("/api/create-page", methods=["POST"])
@login_required
def create_page():
    data = request.get_json()

    project = data.get("project")
    name = data.get("name")
    copy_doc = data.get("copy_doc")
    owner = data.get("owner")
    reviewers = data.get("reviewers")
    parent = data.get("parent")

    owner_id = get_or_create_user_id(owner)

    # Create new webpage
    project_id = get_project_id(project)
    new_webpage = get_or_create(
        db.session,
        Webpage,
        True,
        project_id=project_id,
        name=name,
        url=name,
        parent_id=get_webpage_id(parent, project_id),
        owner_id=owner_id,
        status=WebpageStatus.NEW,
    )

    # Create new reviewer rows
    for reviewer in reviewers:
        reviewer_id = get_or_create_user_id(reviewer)
        get_or_create(
            db.session,
            Reviewer,
            user_id=reviewer_id,
            webpage_id=new_webpage[0].id
        )

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
