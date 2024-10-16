from webapp.models import JiraTask, User, Project, Webpage, db, get_or_create


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


def get_project_id(project_name):
    project = Project.query.filter_by(name=project_name).first()
    return project.id if project else None


def get_webpage_id(name, project_id):
    webpage = Webpage.query.filter_by(name=name, project_id=project_id).first()
    return webpage.id if webpage else None


def convert_webpage_to_dict(webpage, owner, project):
    # Preload relationships
    webpage.reviewers
    webpage.jira_tasks
    webpage.owner
    webpage.project

    webpage_dict = webpage.__dict__.copy()

    # Remove unnecessary fields
    webpage_dict.pop("_sa_instance_state", None)
    webpage_dict.pop("owner_id", None)
    webpage_dict.pop("project_id", None)
    owner = webpage_dict.pop("owner", None)
    project = webpage_dict.pop("project", None)
    reviewers = webpage_dict.pop("reviewers", None)

    # Serialize owner fields
    if owner:
        owner_dict = owner.__dict__.copy()
        owner_dict["created_at"] = owner.created_at.isoformat()
        owner_dict["updated_at"] = owner.updated_at.isoformat()
        if owner_dict["_sa_instance_state"]:
            owner_dict.pop("_sa_instance_state", None)
    else:
        owner_dict = {}

    # Serialize project fields
    if project:
        project_dict = project.__dict__.copy()
        project_dict["created_at"] = project.created_at.isoformat()
        project_dict["updated_at"] = project.updated_at.isoformat()
        if project_dict["_sa_instance_state"]:
            project_dict.pop("_sa_instance_state", None)
    else:
        project_dict = {}

    # Serialize reviewers fields
    if reviewers:
        reviewers_list = []
        for reviewer in reviewers:
            reviewer_dict = reviewer.__dict__.copy()
            reviewer_dict.pop("_sa_instance_state", None)
            reviewer_dict["created_at"] = reviewer.created_at.isoformat()
            reviewer_dict["updated_at"] = reviewer.updated_at.isoformat()
            # Expand the user object
            reviewer_user_dict = reviewer.user.__dict__.copy()
            reviewer_user_dict.pop("created_at")
            reviewer_user_dict.pop("updated_at")
            if reviewer_user_dict["_sa_instance_state"]:
                reviewer_user_dict.pop("_sa_instance_state", None)
            reviewer_dict = {**reviewer_dict, **reviewer_user_dict}
            reviewers_list.append(reviewer_dict)
    else:
        reviewers_list = []

    # Serialize object fields
    webpage_dict["status"] = webpage.status.value
    webpage_dict["created_at"] = webpage.created_at.isoformat()
    webpage_dict["updated_at"] = webpage.updated_at.isoformat()
    webpage_dict["owner"] = owner_dict
    webpage_dict["project"] = project_dict
    webpage_dict["reviewers"] = reviewers_list

    return webpage_dict


def create_copy_doc(app, webpage):
    client = app.config["gdrive"]
    task = client.create_copydoc_from_template(webpage)
    return f"https://docs.google.com/document/d/{task['id']}" if task else None


# recursively build tree from webpages table rows
def build_tree(session, page, webpages):
    child_pages = list(filter(lambda p: p.parent_id == page["id"], webpages))
    for child_page in child_pages:
        project = get_or_create(
            session, Project, id=child_page.project_id
        )
        owner = get_or_create(
            session, User, id=child_page.owner_id
        )
        new_child = convert_webpage_to_dict(child_page, owner, project)
        new_child["children"] = []
        page["children"].append(new_child)
        build_tree(session, new_child, webpages)


def get_tree_struct(session, webpages):
    webpages_list = list(webpages)
    parent_page = next(
        filter(lambda p: p.parent_id is None, webpages_list),
        None
    )

    if (parent_page):
        project = get_or_create(
            session, Project, id=parent_page.project_id
        )
        owner = get_or_create(
            session, User, id=parent_page.owner_id
        )
        tree = convert_webpage_to_dict(parent_page, owner, project)
        tree["children"] = []
        build_tree(session, tree, webpages_list)
        return tree

    return None
