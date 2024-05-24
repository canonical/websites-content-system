import json
import os
import re
import subprocess

from webapp.parse_tree import scan_directory


class SiteRepositoryError(Exception):
    """
    Exception raised for errors in the SiteRepository class
    """


class SiteRepository:
    def __init__(self, repository_uri, branch="main", app=None, cache=None):
        self.repository_uri = repository_uri
        self.branch = branch
        self.app = app
        self.cache = cache

        # Don't run setup if the repository tree is cached
        if not self.get_tree_from_cache():
            self.setup_repository(branch)

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
        command_str = self.__sanitize_command__(command_str)
        return self.__decorate_errors__(self.__exec__, msg)(command_str)

    def __check_git_uri__(self, uri):
        """
        Check if the uri is a valid git uri
        """
        if not uri.endswith(".git"):
            raise SiteRepositoryError(
                f"Invalid git uri. {uri} Please confirm that the uri ends with .git"
            )
        if not uri.startswith("https"):
            raise SiteRepositoryError(
                f"Invalid git uri. {uri} Please confirm that the uri uses https"
            )

    def __create_git_uri__(self, uri):
        """
        Create a github url
        """
        repo_org = self.app.config["REPO_ORG"]
        token = self.app.config["GH_TOKEN"]

        # Add token to URI
        re.sub(
            "//github",
            f"//{token}@github",
        )

        return f"{repo_org}/{uri}.git"

    def delete_local_files(self):
        """
        Delete a local folder
        """
        return self.__run__(
            f"rm -rf {self.repo_name}",
            f"Error deleting folder {self.repo_name}",
        )

    def fetch_remote_branches(self):
        """
        Fetch all branches from remote repository
        """
        return self.__run__(
            f"git fetch origin {self.branch}",
            f"Error fetching branch {self.branch}",
        )

    def clone_repo(self):
        """
        Clone the repository.
        """
        github_url = self.__create_git_uri__(self.repository_uri)
        self.__check_git_uri__(github_url)
        return self.__run__(
            f"git clone {github_url}", f"Error cloning repository {github_url}"
        )

    def checkout_branch(self, branch):
        """
        Checkout the branch
        """
        self.fetch_remote_branches()
        return self.__run__(
            f"git checkout {branch}", f"Error checking out branch {branch}"
        )

    def pull_updates(self):
        """
        Pull updates from the repository
        """
        # Fetch upstream changes
        self.fetch_remote_branches()
        # Pull updates from the specified branch
        self.__run__(
            f"git pull origin {self.branch}",
            "Error pulling updates from repository",
        )

    def setup_repository(self, branch):
        """
        Create the repository on disk
        """
        # Switch to the /tmp directory for cloned repositories
        os.chdir("/tmp")
        self.repo_name = (
            self.repository_uri.strip("/").split("/")[-1].removesuffix(".git")
        )
        # Clone the repository
        self.clone_repo()
        os.chdir(self.repo_name)
        # Checkout the branch
        self.checkout_branch(branch)
        # Retrieve updates
        self.pull_updates()

    def get_tree_from_cache(self):
        """
        Get the tree from the cache. Return None if cache is not available.
        """
        if self.cache:
            if cached_tree := self.cache.get(
                f"{self.repository_uri}/{self.branch}"
            ):
                return json.loads(cached_tree.decode("utf-8"))

    def set_tree_in_cache(self, tree):
        """
        Set the tree in the cache. Silently pass if cache is not available.
        """
        if self.cache:
            return self.cache.set(
                f"{self.repository_uri}/{self.branch}", json.dumps(tree)
            )

    def get_tree_from_disk(self, folder="templates"):
        """
        Get the tree from the repository
        """
        # Check if the templates folder exists
        if not os.path.exists(folder):
            raise SiteRepositoryError(f"Templates folder '{folder}' not found")
        # Change directory to the templates folder
        os.chdir(folder)
        # Parse the templates
        tree = scan_directory(os.getcwd())
        return tree

    def get_new_tree(self):
        """
        Get the tree from the repository and update the cacahe
        """
        tree = self.get_tree_from_disk()
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

        return self.get_new_tree()
