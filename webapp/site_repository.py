import os
import re
import subprocess
import time
from multiprocessing import Lock, Process
from pathlib import Path
from typing import Callable, TypedDict

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.exc import SQLAlchemyError

from webapp.models import Project, User, Webpage, db, get_or_create
from webapp.parse_tree import scan_directory


class SiteRepositoryError(Exception):
    """
    Exception raised for errors in the SiteRepository class
    """


class Tree(TypedDict):
    name: str
    title: str
    description: str
    link: str
    children: list


class SiteRepository:
    # Directory to clone repositories
    CACHE_KEY_PREFIX = "SITE_REPOSITORY"

    LOCKS: dict = {}
    db: SQLAlchemy = db

    def __init__(
        self,
        repository_uri: str,
        app: Flask,
        branch="main",
        task_locks: dict = None,
        db: SQLAlchemy = None,
    ):
        base_dir = app.config["BASE_DIR"]
        self.REPOSITORY_DIRECTORY = f"{base_dir}/repositories"
        self.repository_uri = repository_uri
        self.cache_key = f"{self.CACHE_KEY_PREFIX}_{repository_uri}_{branch}"
        self.branch = branch
        self.app = app
        self.logger = app.logger
        self.cache = app.config["CACHE"]
        self.repo_path = self.get_repo_path(repository_uri)

        # If a database is provided, use it
        if db:
            self.db = db

        # If a locks dictionary is provided, use it
        if task_locks:
            self.LOCKS = task_locks

        # Start the task to load the tree
        self.start_tree_task()

    def __str__(self) -> str:
        return f"SiteRepository({self.repository_uri}, {self.branch})"

    def get_repo_path(self, repository_uri: str):
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
            "git config --global http.postBuffer 1040M",
            "Error configuring git",
        )

    def __exec__(self, command_str: str):
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

    def __decorate_errors__(self, func: Callable, msg: str):
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

    def __sanitize_command__(self, command_str: str):
        """
        Sanitize the command string
        """
        command_str = command_str.strip()
        return re.sub(r"[(\;\|\|\&|\n)]|", "", command_str)

    def __run__(self, command_str: str, msg="Error executing command: "):
        """Execute a sanitized command"""
        self.logger.info(
            f"exec: {command_str}",
        )
        command_str = self.__sanitize_command__(command_str)
        return self.__decorate_errors__(self.__exec__, msg)(command_str)

    def __check_git_uri__(self, uri: str):
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

    def __create_git_uri__(self, uri: str):
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

    def fetch_remote_branch(self, branch: str):
        """
        Fetch all branches from remote repository
        """
        return self.__run__(
            f"git fetch origin {branch}",
            f"Error fetching branch {branch}",
        )

    def clone_repo(self, repository_uri: str):
        """
        Clone the repository.
        """
        github_url = self.__create_git_uri__(repository_uri)
        self.__check_git_uri__(github_url)
        return self.__run__(
            f"git clone {github_url}", f"Error cloning repository {github_url}"
        )

    def checkout_branch(self, branch: str):
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

    def setup_site_repository(self):
        """
        Clone the repository to a specific directory, or checkout the latest
        updates if the repository exists.
        """
        # Create the default repository on disk
        Path(self.REPOSITORY_DIRECTORY).mkdir(parents=True, exist_ok=True)

        # Clone the repository, if it doesn't exist
        if not self.repository_exists():
            # Switch to the ./repositories directory for cloned repositories
            os.chdir(self.REPOSITORY_DIRECTORY)
            self.__configure_git__()
            self.clone_repo(self.repository_uri)
            # Configure git immediately after cloning
            os.chdir(self.repo_path)

        # Checkout updates to the repository on the specified branch
        self.checkout_updates()

    def checkout_updates(self):
        """
        Checkout updates to the repository on the specified branch.
        """
        os.chdir(self.repo_path)
        # Checkout the branch
        self.checkout_branch(self.branch)

    def repository_exists(self):
        """
        Check if the repository exists
        """
        absolute_path = (
            self.app.config["BASE_DIR"]
            + "/repositories/"
            + self.repository_uri
            + "/.git"
        )
        return os.path.exists(absolute_path)

    def get_tree_from_cache(self):
        """
        Get the tree from the cache. Return None if cache is not available.
        """
        if self.cache:
            if cached_tree := self.cache.get(self.cache_key):
                return cached_tree

    def set_tree_in_cache(self, tree):
        """
        Set the tree in the cache. Silently pass if cache is not available.
        """
        if self.cache:
            return self.cache.set(self.cache_key, tree)

    def get_tree_from_disk(self):
        """
        Get a tree from a freshly cloned repository.
        """
        # Setup the repository
        self.setup_site_repository()

        templates_folder = self.repo_path + "/templates"
        # Check if the templates folder exists
        if not os.path.exists(templates_folder):
            raise SiteRepositoryError(
                "Templates folder 'templates' not found for "
                f"repository {self.repo_path}"
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

    def get_new_tree(self):
        """
        Get the tree from the repository, update the cache and save to the
        database.

        """
        # Generate the tree from the repository
        tree = self.get_tree_from_disk()

        # Save the tree metadata to the database
        self.save_tree_to_db(self.db, tree)

        # Update the cache
        self.set_tree_in_cache(tree)
        self.logger.info(f"Tree loaded for {self.repository_uri}")
        return tree

    def get_tree(self):
        """
        Get the tree from the cache or load a new tree to cache and db.
        """
        # Return from cache if available
        if tree := self.get_tree_from_cache():
            return tree

        return self.get_new_tree()

    def start_tree_task(self):
        """
        Start a new task to setup the repository and load the tree.
        """

        def load_tree(lock, logger):
            if lock.acquire(block=False):
                logger.info(f"Loading {self.repository_uri}")
                # Load the tree
                try:
                    self.get_new_tree()
                except Exception as e:
                    logger.error(f"Error loading tree: {e}")
                    # Clean the repository if an error occurs
                    self.delete_local_files()
                finally:
                    lock.release()

        lock = self.get_task_lock()
        Process(
            target=load_tree,
            args=(lock, self.logger),
        ).start()

    def save_tree_to_db(self, db: SQLAlchemy, tree: Tree):
        """
        Save the tree to the database.

        "templates": {
            name -> Webpage.name
            title -> Webpage.title
            description -> Webpage.description
            link -> Webpage.copydoc_link
            ../"id" -> Webpage.parent_id
        },
        """
        # Get or create the default project and owner
        project, _ = get_or_create(
            db.session, Project, name=self.repository_uri
        )
        owner, _ = get_or_create(db.session, User, name="Default")

        def save_child_templates_to_db(parent_id, children):
            """
            Recursively save child templates to the database.
            """
            for child in children:
                if child.get("name"):
                    # Get an existing page for this project or create a new one
                    child_page, created = get_or_create(
                        db.session,
                        Webpage,
                        name=child["name"],
                        url=child["name"],
                        commit=False,
                    )
                    # If instance is new, update the fields
                    if created:
                        child_page.title = child["title"]
                        child_page.description = child["description"]
                        child_page.copy_doc_link = child["link"]
                        child_page.parent_id = parent_id
                        child_page.owner_id = owner.id
                        child_page.project_id = project.id
                if children := child.get("children"):
                    save_child_templates_to_db(child_page.id, children)

        # Get the webpage for the base template
        base_page, created = get_or_create(
            db.session,
            Webpage,
            commit=False,
            name=self.repository_uri,
        )
        # If the base page is new, update the fields
        if created:
            base_page.title = tree["title"]
            base_page.description = tree["description"]
            base_page.copy_doc_link = tree["link"]
            base_page.url = "/"
            base_page.project_id = project.id
            base_page.owner_id = owner.id
        db.session.add(base_page)

        # Save child templates to the database
        save_child_templates_to_db(base_page.id, tree["children"])

        try:
            db.session.commit()
        except SQLAlchemyError as e:
            db.session.rollback()
            raise SiteRepositoryError(f"Error saving tree to database: {e}")

    def __wait_for_tree__(self, timeout=5):
        """
        Wait for the tree to finish generating.
        """
        end = time.time() + timeout
        while time.time() < end:
            if tree := self.get_tree_from_cache():
                return tree
            time.sleep(0.1)

    def get_tree_async(self):
        """
        Try to get the tree from the cache, or create a new task to load it.
        """
        # First try to get the tree from the cache
        if tree := self.get_tree_from_cache():
            return tree

        # Otherwise, create a new task to load the tree
        self.start_tree_task()

        # Wait for the tree to be ready in 3s
        if tree := self.__wait_for_tree__(timeout=3):
            return tree

        # Or just return an empty tree
        return {
            "name": "",
            "title": "",
            "description": "",
            "link": "",
            "children": [],
        }

    def get_task_lock(self):
        """
        Get the lock for the current repository.
        """
        if lock := self.LOCKS.get(self.repository_uri):
            return lock
        # If a lock doesn't exist, create one
        self.LOCKS[self.repository_uri] = Lock()
        return self.LOCKS[self.repository_uri]

    def get_webpages(self):
        """
        Return a list of webpages from the associated parsed tree.
        """
        tree = self.get_tree()
        webpages = []

        def add_pages_to_list(tree, page_list: list):
            # Append root node name
            page_list.append(tree["name"])
            for child in tree["children"]:
                page_list.append(child["name"])
                # If child nodes exist, add their names to the list
                if child.get("children"):
                    add_pages_to_list(child, page_list)

        add_pages_to_list(tree, webpages)
        return webpages
