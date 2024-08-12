import json
import os
import re
import subprocess
from pathlib import Path

from webapp.parse_tree import scan_directory


class SiteRepositoryError(Exception):
    """
    Exception raised for errors in the SiteRepository class
    """

def site_repository_exists(app, repo_path):
    """
    Check if the site repository exists
    """
    absolute_path = app.config["BASE_DIR"] + "/repositories/" + repo_path
    return os.path.exists(absolute_path)

class SiteRepository:

    # Directory to clone repositories
    CACHE_KEY_PREFIX = "SITE_REPOSITORY"

    def __init__(self, repository_uri, branch="main", app=None, cache=None):
        base_dir = app.config["BASE_DIR"]
        self.REPOSITORY_DIRECTORY = f"{base_dir}/repositories"
        self.repository_uri = repository_uri
        self.cache_key = f"{self.CACHE_KEY_PREFIX}_{repository_uri}_{branch}"
        self.branch = branch
        self.app = app
        self.logger = app.logger
        self.cache = cache
        self.repo_path = self.get_repo_path(repository_uri)

        # Don't run setup if the repository exists
        if not self.repository_exists(repository_uri):
            self.setup_repository(repository_uri, branch)

    def __str__(self) -> str:
        return f"SiteRepository({self.repository_uri}, {self.branch})"

    def get_repo_path(self, repository_uri):
        """
        Get the repository path
        """
        return (
            self.REPOSITORY_DIRECTORY
            + "/"
            + (repository_uri.strip("/").split("/")[-1].removesuffix(".git"))
        )

    def __configure_git__(self):
        """
        Update git configuration.
        """
        # Increase the buffer size for large files
        self.__run__(
            "git config http.postBuffer 52428800",
            "Error configuring git",
        )
        # Disable compression
        self.__run__(
            "git config core.compression 0",
            "Error configuring git",
        )

    def __exec__(self, command_str):
        """
        Execute a command and return the output
        """
        command = command_str.strip("").split(" ")
        process = subprocess.Popen(
            command, stdout=subprocess.PIPE, stderr=subprocess.PIPE
        )
        # Wait for the process to finish
        process.wait()
        stdout, stderr = process.communicate()
        if process.returncode != 0:
            raise OSError(f"Execution Error: {stderr.decode('utf-8')}")
        return stdout.decode("utf-8")

    def __decorate_errors__(self, func, msg):
        """
        Decorator to catch OSError and raise SiteRepositoryError
        """

        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except OSError as e:
                # Silently ignore "directory already exists" errors
                if re.search(r"destination path (.*) already exists", str(e)):
                    return 0
                raise SiteRepositoryError(f"{msg}: {e}")

        return wrapper

    def __sanitize_command__(self, command_str):
        """
        Sanitize the command string
        """
        command_str = command_str.strip()
        return re.sub(r"[(\;\|\|\&|\n)]|", "", command_str)

    def __run__(self, command_str, msg="Error executing command: "):
        """Execute a sanitized command"""
        self.logger.info(
            f"exec: {command_str}",
        )
        command_str = self.__sanitize_command__(command_str)
        return self.__decorate_errors__(self.__exec__, msg)(command_str)

    def __check_git_uri__(self, uri):
        """
        Check if the uri is a valid git uri
        """
        if not uri.endswith(".git"):
            raise SiteRepositoryError(
                f"Invalid git uri. {uri} Please confirm "
                "that the uri ends with .git"
            )
        if not uri.startswith("https"):
            raise SiteRepositoryError(
                f"Invalid git uri. {uri} Please confirm "
                "that the uri uses https"
            )

    def __create_git_uri__(self, uri):
        """
        Create a github url
        """
        repo_org = self.app.config["REPO_ORG"]
        token = self.app.config["GH_TOKEN"]

        # Add token to URI
        uri = re.sub(
            "//github",
            f"//{token}@github",
            uri,
        )

        return f"{repo_org}/{uri}.git"

    def delete_local_files(self):
        """
        Delete a local folder
        """
        return self.__run__(
            f"rm -rf {self.repo_path}",
            f"Error deleting folder {self.repo_path}",
        )

    def fetch_remote_branch(self, branch):
        """
        Fetch all branches from remote repository
        """
        return self.__run__(
            f"git fetch origin {branch}",
            f"Error fetching branch {branch}",
        )

    def clone_repo(self, repository_uri=None):
        """
        Clone the repository.
        """
        github_url = self.__create_git_uri__(repository_uri)
        self.__check_git_uri__(github_url)
        return self.__run__(
            f"git clone {github_url}", f"Error cloning repository {github_url}"
        )

    def checkout_branch(self, branch):
        """
        Checkout the branch
        """
        self.fetch_remote_branch(branch)
        return self.__run__(
            f"git checkout {branch}", f"Error checking out branch {branch}"
        )

    def pull_updates(self):
        """
        Pull updates from the repository
        """
        # Pull updates from the specified branch
        self.__run__(
            f"git pull origin {self.branch}",
            "Error pulling updates from repository",
        )

    def setup_repository_directory(self, repository_uri):
        """
        Clone the repository to a specific directory.
        """
        # Create the default repository on disk
        Path(self.REPOSITORY_DIRECTORY).mkdir(parents=True, exist_ok=True)
        # Switch to the ./repositories directory for cloned repositories
        os.chdir(self.REPOSITORY_DIRECTORY)
        # Clone the repository
        self.clone_repo(repository_uri)

    def checkout_updates(self, repo_path, branch):
        """
        Checkout updates to the repository on the specified branch.
        """
        os.chdir(repo_path)
        # Checkout the branch
        self.checkout_branch(branch)

    def repository_exists(self, repo_path):
        """
        Check if the repository exists
        """
        return site_repository_exists(self.app, repo_path)

    def setup_repository(self, repository_uri, branch):
        """
        Create the repository on disk
        """
        repo_path = self.get_repo_path(repository_uri)
        self.setup_repository_directory(repository_uri)
        self.__configure_git__()
        self.checkout_updates(repo_path, branch)

    def get_tree_from_cache(self):
        """
        Get the tree from the cache. Return None if cache is not available.
        """
        if self.cache:
            if cached_tree := self.cache.get(self.cache_key):
                return json.loads(cached_tree)

    def set_tree_in_cache(self, tree):
        """
        Set the tree in the cache. Silently pass if cache is not available.
        """
        if self.cache:
            return self.cache.set(
                self.cache_key,
                json.dumps(tree),
            )

    def get_tree_from_disk(self, repo_path, branch):
        """
        Get the tree from the repository
        """
        self.checkout_updates(repo_path, branch)
        templates_folder = repo_path + "/templates"
        # Check if the templates folder exists
        if not os.path.exists(templates_folder):
            raise SiteRepositoryError(
                "Templates folder 'templates' not found for "
                f"repository {repo_path}"
            )
        # Change directory to the templates folder
        os.chdir(templates_folder)
        # Parse the templates
        try:
            tree = scan_directory(os.getcwd())
        except Exception as e:
            raise SiteRepositoryError(f"Error scanning directory: {e}")
        finally:
            # Change back to the root directory
            os.chdir("../../..")
        return tree

    def get_new_tree(self, repo_path, branch):
        """
        Get the tree from the repository and update the cacahe
        """
        tree = self.get_tree_from_disk(repo_path, branch)
        # Update the cache
        self.set_tree_in_cache(tree)
        return tree

    def get_tree(self):
        """
        Get the tree from the cache or a fresh copy.
        """
        # Return from cache if available
        if tree := self.get_tree_from_cache():
            return tree

        return self.get_new_tree(self.repo_path, self.branch)
