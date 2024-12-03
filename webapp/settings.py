import base64
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
GOOGLE_CREDENTIALS = {
    "type": "service_account",
    "project_id": "web-engineering-436014",
    "private_key_id": environ.get("GOOGLE_PRIVATE_KEY_ID"),
    "private_key": base64.b64decode(environ.get("GOOGLE_PRIVATE_KEY")).replace(
        b"\\n", b"\n"
    ),
    "client_email": "websites-copy-docs-627@web-engineering-436014.iam.gserviceaccount.com",  # noqa: E501
    "client_id": "116847960229506342511",
    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
    "token_uri": "https://oauth2.googleapis.com/token",
    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/websites-copy-docs-627%40web-engineering-436014.iam.gserviceaccount.com",  # noqa: E501
    "universe_domain": "googleapis.com",
}
DEVELOPMENT_MODE = environ.get("DEVEL", True)