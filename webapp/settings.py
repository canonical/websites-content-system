import os
from os import environ

VALKEY_HOST = environ.get("VALKEY_HOST", "localhost")
VALKEY_PORT = environ.get("VALKEY_PORT", 6379)
REPO_ORG = environ.get("REPO_ORG", "https://github.com/canonical")
GH_TOKEN = environ.get("GH_TOKEN", "")
SECRET_KEY = environ.get("SECRET_KEY")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLALCHEMY_DATABASE_URI = environ.get("DATABASE_URL", "sqlite:///project.db")
JIRA_EMAIL = environ.get("JIRA_EMAIL")
JIRA_TOKEN = environ.get("JIRA_TOKEN")
JIRA_URL = environ.get("JIRA_URL")
JIRA_LABELS = environ.get("JIRA_LABELS")
JIRA_COPY_UPDATES_EPIC = environ.get("JIRA_COPY_UPDATES_EPIC")
GOOGLE_DRIVE_FOLDER_ID = environ.get("GOOGLE_DRIVE_FOLDER_ID")
COPYD0C_TEMPLATE_ID = environ.get("COPYD0C_TEMPLATE_ID")
GOOGLE_SERVICE_ACCOUNT = environ.get("GOOGLE_SERVICE_ACCOUNT")