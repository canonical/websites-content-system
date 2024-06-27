from os import environ

REDIS_HOST = environ.get("REDIS_HOST", "localhost")
REDIS_PORT = environ.get("REDIS_PORT", 6379)
REPO_ORG = environ.get("REPO_ORG", "https://github.com/canonical")
GH_TOKEN = environ.get("GH_TOKEN", "")
SECRET_KEY = environ.get("SECRET_KEY")