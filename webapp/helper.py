from webapp.gdrive import GoogleDriveClient
from webapp.models import JiraTask, User, Webpage, db, get_or_create


def get_or_create_user_id(user):
    # If user does not exist, create a new user in the "users" table
    user_hrc_id = user.get("id")
    user_exists = User.query.filter_by(hrc_id=user_hrc_id).first()
    if not user_exists:
        user_exists, _ = get_or_create(
            db.session,
            User,
            name=user.get("name"),
            email=user.get("email"),
            team=user.get("team"),
            department=user.get("department"),
            job_title=user.get("jobTitle"),
            hrc_id=user_hrc_id,
        )

    return user_exists.id


def create_jira_task(app, task):
    """
    Create a new issue on jira and add a record to the db
    """
    # TODO: If an epic already exists for this request, add subtasks to it.

    jira = app.config["JIRA"]
    issue = jira.create_issue(
        due_date=task["due_date"],
        reporter_id=task["reporter_id"],
        webpage_id=task["webpage_id"],
        request_type=task["type"],
        description=task["description"],
    )

    # Create jira task in the database
    get_or_create(
        db.session,
        JiraTask,
        jira_id=issue["key"],
        webpage_id=task["webpage_id"],
        user_id=task["reporter_id"],
    )

    # Create a new copydoc if the request is a new webpage
    if task["type"] == jira.NEW_WEBPAGE:
        webpage = Webpage.query.filter_by(id=task["webpage_id"]).first()
        client = GoogleDriveClient(
            credentials=app.config["GOOGLE_SERVICE_ACCOUNT"],
            drive_folder_id=app.config["GOOGLE_DRIVE_FOLDER_ID"],
            copydoc_template_id=app.config["COPYD0C_TEMPLATE_ID"],
        )
        client.create_copydoc_from_template(webpage)
