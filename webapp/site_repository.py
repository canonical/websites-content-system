import os
import re
import subprocess
from multiprocessing import Lock
from pathlib import Path
from typing import Callable, TypedDict

from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import select, delete

from webapp.models import (
  Project, User, Webpage, db, get_or_create, WebpageStatus
)
from webapp.parse_tree import scan_directory
from webapp.helper import (
  get_project_id, get_tree_struct, convert_webpage_to_dict
)


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
        db: SQLAlchemy = None
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
            try:
                self.__configure_git__()
            except SiteRepositoryError as e:
                self.logger.error(e)
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

    def invalidate_cache(self):
        self.cache.set(self.cache_key, None)

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
        # Generate the base tree from the repository
        base_tree = self.get_tree_from_disk()

        # Save the tree metadata to the database and return an updated tree
        # that has all fields
        tree = self.create_webpages_for_tree(self.db, base_tree)

        self.logger.info(f"Tree loaded for {self.repository_uri}")
        return tree

    def get_tree_from_db(self):
        webpages = self.db.session.execute(
            select(Webpage).where(
                Webpage.project_id == get_project_id(self.repository_uri)
            )
        ).scalars()
        # build tree from repository in case DB table is empty
        if not webpages:
            self.get_new_tree()

        tree = get_tree_struct(db.session, webpages)

        self.logger.info(f"Tree fetched for {self.repository_uri}")

        return tree

    def get_tree(self, no_cache: bool = False):
        """
        Get the tree from the cache or load a new tree to cache and db.
        """
        # Return from cache if available
        if not no_cache:
            if tree := self.get_tree_from_cache():
                return tree

        return self.get_new_tree()

    def __create_webpage_for_node__(
        self,
        db: SQLAlchemy,
        node: dict,
        project: Project,
        owner: User,
        parent_id: int,
    ):
        """
        Create a webpage from a node in the tree.
        """
        # Get a webpage for this name and project, or create a new one
        webpage, created = get_or_create(
            db.session,
            Webpage,
            name=node["name"],
            url=node["name"],
            project_id=project.id,
            commit=False,
        )

        # If instance is new, update the owner and project fields
        if created:
            webpage.owner_id = owner.id
            webpage.project_id = project.id

        # Update the fields
        webpage.title = node["title"]
        webpage.description = node["description"]
        webpage.copy_doc_link = node["link"]
        webpage.parent_id = parent_id
        if webpage.status == WebpageStatus.NEW:
            webpage.status = WebpageStatus.AVAILABLE

        db.session.add(webpage)
        db.session.flush()

        webpage_dict = convert_webpage_to_dict(webpage, owner, project)

        # Return a dict with the webpage fields
        return {**node, **webpage_dict}

    def __create_webpages_for_children__(
        self, db, children, project, owner, parent_id
    ):
        """
        Recursively create webpages for each child in the tree.
        """
        for child in children:
            # Create a webpage for the root node
            webpage_dict = self.__create_webpage_for_node__(
                db, child, project, owner, parent_id
            )
            # Update the child node with the webpage fields
            child.update(webpage_dict)
            if child.get("children"):
                # Create webpages for the children recursively
                self.__create_webpages_for_children__(
                    db, child["children"], project, owner, webpage_dict["id"]
                )

    def __remove_webpages_to_delete__(self, db, tree):
        # convert tree of pages from repository to list
        webpages = []
        self.add_pages_to_list(tree, webpages)

        webpages_to_delete = db.session.execute(
            select(Webpage).where(Webpage.status == WebpageStatus.TO_DELETE)
        )

        for row in webpages_to_delete:
            page_to_delete = row[0]
            if page_to_delete.name not in webpages:
                db.session.execute(
                    delete(Webpage).where(Webpage.id == page_to_delete.id)
                )

    def create_webpages_for_tree(self, db: SQLAlchemy, tree: Tree):
        """
        Create webpages for each node in the tree.
        """
        # Get the default project and owner for new webpages
        project, _ = get_or_create(
            db.session, Project, name=self.repository_uri
        )
        owner, _ = get_or_create(db.session, User, name="Default")

        # Create a webpage for the root node
        webpage_dict = self.__create_webpage_for_node__(
            db, tree, project, owner, None
        )

        # Create webpages for the children recursively
        self.__create_webpages_for_children__(
            db, webpage_dict["children"], project, owner, webpage_dict["id"]
        )

        # Remove pages that don't exist in the repository anymore
        self.__remove_webpages_to_delete__(db, tree)

        db.session.commit()
        return webpage_dict

    def get_tree_sync(self, no_cache: bool = False):
        """
        Try to get the tree from the cache, or create a new task to load it.
        """
        # First try to get the tree from the cache
        if not no_cache:
            if tree := self.get_tree_from_cache():
                return tree
        else:
            self.invalidate_cache()

        self.logger.info(f"Loading {self.repository_uri} from database")
        # Load the tree from database
        try:
            tree = self.get_tree_from_db()
            # Update the cache
            self.set_tree_in_cache(tree)
            return tree
        except Exception as e:
            self.logger.error(f"Error loading tree: {e}")

        # Or just return an empty tree
        return {
            "name": "",
            "title": "",
            "description": "",
            "copy_doc_link": "",
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

    def add_pages_to_list(self, tree, page_list: list):
        # Append root node name
        page_list.append(tree["name"])
        for child in tree["children"]:
            page_list.append(child["name"])
            # If child nodes exist, add their names to the list
            if child.get("children"):
                self.add_pages_to_list(child, page_list)

    def get_webpages(self):
        """
        Return a list of webpages from the associated parsed tree.
        """
        tree = self.get_tree()
        webpages = []
        self.add_pages_to_list(tree, webpages)
        return webpages
