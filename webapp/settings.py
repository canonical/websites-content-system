import os
from os import environ

VALKEY_HOST = environ.get("VALKEY_HOST", "localhost")
VALKEY_PORT = environ.get("VALKEY_PORT", 6379)
REPO_ORG = environ.get("REPO_ORG", "https://github.com/canonical")
GH_TOKEN = environ.get("GH_TOKEN", "")
SECRET_KEY = environ.get("SECRET_KEY")
BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SQLALCHEMY_DATABASE_URI = environ.get(
    "SQLALCHEMY_DATABASE_URI", "sqlite:///project.db"
)