from __future__ import annotations

import json
from datetime import datetime

import requests
from requests.auth import HTTPBasicAuth

from webapp.models import User, Webpage, db


class Jira:
    headers = {
        "Accept": "application/json",
        "Content-Type": "application/json",
    }
    EPIC = "10000"
    SUBTASK = "10013"
    COPY_UPDATE = 0
    PAGE_REFRESH = 1
    NEW_WEBPAGE = 2

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

        if response.status_code in [200, 201, 204]:
            try:
                return response.json()
            except json.JSONDecodeError:
                return {
                    "status_code": response.status_code,
                    "response": response.text or "No response",
                }

        raise Exception(
            "Failed to make a request to Jira. Status code:"
            f" {url} {method} {data} {params}"
            f" {response.status_code}. Response: {response.text}"
        )

    def get_reporter_jira_id(self, user_id):
        """
        Get the Jira ID of the user who reported the issue.

        Args:
            user_id (int): The ID of the user who reported the issue.

        Returns:
            str: The Jira ID of the user who reported the issue.
        """
        # Try to get the user from the database
        user = db.session.query(User).filter_by(id=user_id).first()
        if not user:
            raise ValueError(f"User with ID {user_id} not found")
        # If the user already has a Jira account ID, return it
        if user.jira_account_id:
            return user.jira_account_id
        # Otherwise get it from jira
        jira_user = self.find_user(user.email)
        if not jira_user:
            raise ValueError(f"User with email {user.email} not found in Jira")
        # Update the user in the database
        user.jira_account_id = jira_user[0]["accountId"]
        db.session.commit()
        return jira_user[0]["accountId"]

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
        reporter_jira_id: str,
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
            reporter_jira_id (str): The ID of the reporter of the task.
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
                "reporter": {"id": reporter_jira_id},
                "parent": parent,
                "duedate": due_date,
                "project": {"id": "10492"},  # Web and Design-ENG
                "components": [
                    {"id": "12655"},  # Sites Tribe
                ],
            },
            "update": {},
        }
        return self.__request__(
            method="POST", url=f"{self.url}/rest/api/3/issue", data=payload
        )

    def create_issue(
        self,
        request_type: int,
        description: str,
        reporter_id: str,
        webpage_id: int,
        due_date: datetime,
        summary: str,
    ):
        """Creates a new issue in Jira.

        Args:
            request_type (int): The type of the request. 0 for Epic, 1 or 2 for
                Task.
            description (str): The description of the issue.
            reporter_id (str): The ID of the reporter.
            webpage_id (int): The ID of the webpage.
            due_date (datetime): The due date of the issue.

        Returns:
            dict: The response from the Jira API.
        """
        # Get the webpage
        webpage = Webpage.query.filter_by(id=webpage_id).first()
        if not webpage:
            raise Exception(f"Webpage with ID {webpage_id} not found")

        # Get the reporter ID
        reporter_jira_id = self.get_reporter_jira_id(reporter_id)

        # Determine summary message
        if request_type == self.COPY_UPDATE:
            summary = f"Copy update {webpage.name}"
        elif request_type == self.PAGE_REFRESH:
            summary = f"Page refresh for {webpage.name}"
        elif request_type == self.NEW_WEBPAGE:
            summary = f"New webpage for {webpage.name}"

        # Create the issue depending on the request type
        if (
            request_type == self.NEW_WEBPAGE
            or request_type == self.PAGE_REFRESH
        ):
            # Create epic
            epic = self.create_task(
                summary=summary,
                issue_type=self.EPIC,
                description=description,
                parent=None,
                reporter_jira_id=reporter_jira_id,
                due_date=due_date,
            )

            if not epic:
                raise Exception("Failed to create epic")

            # Create subtasks for this epic
            for subtask_name in ["UX", "Visual", "Dev"]:
                self.create_task(
                    summary=f"{subtask_name} - {summary}",
                    issue_type=self.SUBTASK,
                    description=description,
                    parent=epic["key"],
                    reporter_jira_id=reporter_jira_id,
                    due_date=due_date,
                )
            return epic

        return self.create_task(
            summary=summary,
            issue_type=self.SUBTASK,
            description=description,
            parent=self.copy_updates_epic,
            reporter_jira_id=reporter_jira_id,
            due_date=due_date,
        )

    def change_issue_status(self, issue_id: str, transition_id: str) -> bool:
        """Change the status of a Jira issue.

        Args:
            issue_id (str): The ID of the Jira issue (e.g., "JIRA-123").
            transition_id (str): Transition_ID for the desired status.

        Returns:
            Bool: True if status was changed successfully else False.
        """
        payload = {
            "transition": {"id": transition_id},
        }
        return self.__request__(
            method="POST",
            url=f"{self.url}/rest/api/3/issue/{issue_id}/transitions",
            data=payload,
        )


def init_jira(app):
    app.config["JIRA"] = Jira(
        url=app.config["JIRA_URL"],
        email=app.config["JIRA_EMAIL"],
        token=app.config["JIRA_TOKEN"],
        labels=app.config["JIRA_LABELS"].split(","),
        copy_updates_epic=app.config["JIRA_COPY_UPDATES_EPIC"],
    )
