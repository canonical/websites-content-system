from os import environ

VALKEY_HOST = environ.get("VALKEY_HOST", "localhost")
VALKEY_PORT = environ.get("VALKEY_PORT", 6379)
REPO_ORG = environ.get("REPO_ORG", "https://github.com/canonical")
GH_TOKEN = environ.get("GH_TOKEN", "")
SECRET_KEY = environ.get("SECRET_KEY")