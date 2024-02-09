from os import environ

REDIS_HOST = environ.get("REDIS_HOST", "localhost")
REDIS_PORT = environ.get("REDIS_PORT", 6379)
REPO_ORG = "https://github.com/canonical"
