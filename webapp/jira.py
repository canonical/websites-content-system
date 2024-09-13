from __future__ import annotations

import json
from datetime import datetime
from typing import Literal, Optional

import requests
from pydantic import BaseModel
from requests.auth import HTTPBasicAuth

from webapp.models import User, Webpage


class Issue(BaseModel):
    project: str
    summary: str
    description: str
    priority: str
    issuetype: str


class JIRATaskRequestModel(BaseModel):
    project: Literal["Web & Design - ENG"]
    due_date: datetime
    reporter: str
    components: str
    labels: str
    description: Optional[str] = None


class JIRATaskResponseModel(BaseModel):
    id: int
    age: int
    name: str
    nickname: Optional[str] = None


class Jira:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    EPIC = "10000"
    SUBTASK = "10013"

    def __init__(
        self,
        url: str,
        email: str,
        token: str,
        labels: str,
        copy_updates_epic: str,
    ):
        """
        Initialize the Jira object.

        Args:
            url (str): The URL of the Jira instance.
            email (str): The email address of the user.
            token (str): The API token of the user.
            labels (str): The labels to be applied to the created issues.
            copy_updates_epic (str): The key of the epic to copy updates to.
        """
        self.url = url
        self.auth = HTTPBasicAuth(email, token)
        self.labels = labels
        self.copy_updates_epic = copy_updates_epic

    def __request__(
        self, method: str, url: str, data: dict = {}, params: dict = {}
    ):
        if data:
            data = json.dumps(data)
        response = requests.request(
            method,
            url,
            data=data,
            headers=self.headers,
            auth=self.auth,
            params=params,
        )

        if response.status_code != 200:
            raise Exception(
                "Failed to make a request to Jira. Status code:"
                f" {response.status_code}. Response: {response.text}"
            )

        return response.json()

    def get_reporter_jira_id(self, user_id):
        """
        Get the Jira ID of the user who reported the issue.

        Args:
            user_id (int): The ID of the user who reported the issue.

        Returns:
            str: The Jira ID of the user who reported the issue.
        """
        # Try to get the user from the database
        user = User.query.filter_by(id=user_id).first()
        if user:
            if user.jira_account_id:
                return user.jira_account_id
        # Otherwise get it from jira
        jira_user = self.find_user(user.email)
        if not jira_user:
            raise ValueError(f"User with email {user.email} not found in Jira")
        # Update the user in the database
        # user.jira_account_id = jira_user["accountId"]
        # db.session.commit()
        return jira_user

    def find_user(self, query: str):
        """
        Find a user based on a query.

        Args:
            query (str): The query string to search for a user.

        Returns:
            dict: A dictionary containing the user information.
        """
        return self.__request__(
            method="GET",
            url=f"{self.url}/rest/api/3/user/search",
            params={"query": query},
        )

    def create_task(
        self,
        summary: str,
        issue_type: int,
        description: str,
        parent: str,
        reporter: str,
        due_date: datetime,
    ):
        """
        Creates a task or subtask in Jira.

        Args:
            summary (str): The summary of the task.
            issue_type (int): The ID of the issue type for the task.
            description (str): The description of the task.
            parent (str): The key of the parent issue. If None, the task will
                be created without a parent.
            reporter (str): The ID of the reporter of the task.
            due_date (datetime): The due date of the task.

        Returns:
            dict: The response from the Jira API containing information about
                the created task.
        """
        if parent:
            parent = {"key": parent}

        payload = {
            "fields": {
                "description": {
                    "content": [
                        {
                            "content": [
                                {
                                    "text": description,
                                    "type": "text",
                                }
                            ],
                            "type": "paragraph",
                        }
                    ],
                    "type": "doc",
                    "version": 1,
                },
                "summary": summary,
                "issuetype": {"id": issue_type},
                "labels": self.labels,
                "reporter": {"id": reporter},
                "duedate": due_date.date.isoformat(),
                "parent": parent,
                "project": {"id": "10000"},  # Hardcoded for now
                "components": [{"id": "10000"}],  # Hardcoded for now
            },
            "update": {},
        }
        return self.__request__(
            method="POST", url=f"{self.url}/rest/api/3/issue", data=payload
        )

    def create_issue(
        self,
        issue_type: int,
        description: str,
        reporter: str,
        webpage_id: int,
        due_date: datetime,
    ):
        """Creates a new issue in Jira.

        Args:
            issue_type (int): The type of the issue. 0 for Epic, 1 or 2 for
                Task.
            description (str): The description of the issue.
            reporter (str): The ID of the reporter.
            webpage_id (int): The ID of the webpage.
            due_date (datetime): The due date of the issue.

        Returns:
            dict: The response from the Jira API.
        """
        # Get the webpage
        try:
            webpage = Webpage.query.filter_by(id=webpage_id).first()
            if not webpage:
                raise Exception
        except Exception:
            raise Exception(f"Webpage with ID {webpage_id} not found")

        # Get the reporter ID
        reporter = self.get_reporter_jira_id(reporter)

        # Determine the correct issue type
        if issue_type == 0:
            parent = None
            summary = f"Copy update {webpage.name}"
            # Create epic
            epic = self.create_task(
                summary=None,
                issue_type=self.EPIC,
                description=description,
                parent=parent,
                reporter=reporter,
                due_date=due_date,
            )
            # Create subtasks for this epic
            for subtask_name in ["UX", "Visual", "Dev"]:
                self.create_task(
                    summary=f"{subtask_name}-{summary}",
                    issue_type=self.SUBTASK,  # Task
                    description=description,
                    parent=epic["id"],
                    reporter=reporter,
                    due_date=due_date,
                )
            return epic

        elif issue_type == 1 or issue_type == 2:
            parent = {"key": self.copy_updates_epic}

        # Determine summary message
        if issue_type == 0:
            summary = f"Copy update {webpage.name}"
        elif issue_type == 1:
            summary = f"Page refresh for {webpage.name}"
        elif issue_type == 2:
            summary = f"New webpage for {webpage.name}"

        return self.create_task(
            summary=summary,
            issue_type=self.SUBTASK,
            description=description,
            parent=parent,
            reporter=reporter,
            due_date=due_date,
        )


def init_jira(app):
    app.config["JIRA"] = Jira(
        url=app.config["JIRA_URL"],
        email=app.config["JIRA_EMAIL"],
        token=app.config["JIRA_TOKEN"],
        labels=app.config["JIRA_LABELS"].split(","),
        copy_updates_epic=app.config["JIRA_COPY_UPDATES_EPIC"],
    )
