from flask import jsonify, Blueprint, current_app
from flask_pydantic import validate

from webapp.sso import login_required
from webapp.enums import JiraStatusTransitionCodes
from webapp.site_repository import SiteRepository
from webapp.tasks import LOCKS
from webapp.helper import (
    create_copy_doc,
    create_jira_task,
    get_or_create_user_id,
    get_project_id,
    get_webpage_id,
)
from webapp.models import (
    JiraTask,
    Project,
    Reviewer,
    User,
    Webpage,
    WebpageStatus,
    db,
    get_or_create,
)
from webapp.schemas import (
    ChangesRequestModel,
    CreatePageModel,
    RemoveWebpageModel,
)

jira_blueprint = Blueprint("jira", __name__, url_prefix="/api")


@jira_blueprint.route("/request-changes", methods=["POST"])
@login_required
@validate()
def request_changes(body: ChangesRequestModel):
    # Make a request to JIRA to create a task
    try:
        params = body.model_dump()
        create_jira_task(current_app, params)

        webpage = Webpage.query.filter_by(id=params["webpage_id"]).first()
        project = Project.query.filter_by(id=webpage.project_id).first()
        site_repository = SiteRepository(
            project.name, current_app, task_locks=LOCKS
        )
        # clean the cache for a new Jira task to appear in the tree
        site_repository.invalidate_cache()
    except Exception as e:
        return jsonify(str(e)), 500

    return jsonify({"message": "Task created successfully"}), 201


@jira_blueprint.route("/get-jira-tasks/<webpage_id>", methods=["GET"])
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


@jira_blueprint.route("/remove-webpage", methods=["POST"])
@validate()
@login_required
def remove_webpage(body: RemoveWebpageModel):
    """
    Remove a webpage based on its status.
    This function handles removal of a webpage from the system.
    If the webpage is new and not in the codebase,
    it deletes the webpage and associated
    reviewer records from the database.
    If the webpage pre-exists, it creates Jira task to remove
    the webpage from code repository and updates the webpage
    status to "TO_DELETE".
    Args:
        body (RemoveWebpageModel): The model containing
            the details of the webpage to be removed.
    Returns:
        Response: A JSON response indicating the result
                of the operation.
        - If the webpage is not found, returns a 404 error
            with a message.
        - If the webpage is successfully deleted or a task
            is created,returns a 201 status with
            a success message.
        - If there is an error during deletion,
            returns a 500 error with a message.
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
                    status_change = current_app.config[
                        "JIRA"
                    ].change_issue_status(
                        issue_id=task.jira_id,
                        transition_id=JiraStatusTransitionCodes.REJECTED.value,
                    )
                    if status_change["status_code"] != 204:
                        return (
                            jsonify(
                                {
                                    "error": f"failed to change status of Jira task {task.jira_id}"  # noqa
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
            current_app.logger.info(
                e, "Error deleting webpage from the database"
            )
            return jsonify({"error": "unable to delete the webpage"}), 500

        return (
            jsonify({"message": "Webpage has been removed successfully"}),
            200,
        )

    if webpage.status == WebpageStatus.AVAILABLE:
        if not (
            body.reporter_id
            and User.query.filter_by(id=body.reporter_id).one_or_none()
        ):
            return (
                jsonify({"error": "provided parameters are incorrect"}),
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
        task = create_jira_task(current_app, task_details)
        Webpage.query.filter_by(id=webpage_id).update(
            {"status": WebpageStatus.TO_DELETE.value}
        )
        db.session.commit()

    project = Project.query.filter_by(id=webpage.project_id).first()
    site_repository = SiteRepository(
        project.name, current_app, task_locks=LOCKS
    )
    # clean the cache for a page to be removed from the tree
    site_repository.invalidate_cache()

    return (
        jsonify(
            {"message": f"removal of {webpage.name} processed successfully"}
        ),
        200,
    )


@jira_blueprint.route("/create-page", methods=["POST"])
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
        copy_doc = create_copy_doc(current_app, new_webpage[0])
        new_webpage[0].copy_doc_link = copy_doc
        db.session.commit()

    return jsonify({"copy_doc": copy_doc}), 201
