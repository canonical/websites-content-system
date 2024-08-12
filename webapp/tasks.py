import time
from multiprocessing import Process
from typing import Dict

import yaml
from flask import Flask

from webapp.models import Project, User, Webpage, db
from webapp.site_repository import (
    SiteRepository,
    SiteRepositoryError,
    site_repository_exists,
)

# Keep track of generation tasks for each tree.
TREE_TASKS: Dict[str, Process] = {}

def init_tasks(app: Flask):
    """
    Start event loop.
    """

    @app.before_request
    def start_tasks():
        # Only run once
        app.before_request_funcs[None].remove(start_tasks)
        Process(
            target=load_site_trees,
            args=(app,),
        ).start()


def load_site_trees(app: Flask):
    """
    Load the site trees from the queue.
    """
    while True:
        with open(app.config["BASE_DIR"] + "/" + "sites.yaml") as f:
            data = yaml.safe_load(f)
            for site in data["sites"]:
                add_tree_task(site, "main", app)
        # Wait for 30 minutes before enqueuing the next set of trees
        time.sleep(1800)


def add_tree_task(uri: str, branch: str, app: Flask):
    """
    Put the tree object in the queue.
    """
    # If the tree is already being loaded, return the process.
    if p := TREE_TASKS.get(uri):
        if p.is_alive():
            return p

    app.logger.info(f"Loading {uri}")

    def load_tree():
        try:
            site_repository = SiteRepository(
                uri, branch, app=app, cache=app.config["CACHE"]
            )
            return site_repository.get_tree()
        except SiteRepositoryError as e:
            app.logger.error(f"Error loading {uri}: {e}")
        finally:
            TREE_TASKS.pop(uri, "")

    # Start the process to load the tree, and add it to the map.
    p = Process(target=load_tree)
    p.start()
    TREE_TASKS[uri] = p
    return p


def get_tree_async(uri: str, branch: str, app: Flask):
    """
    Async process to enqueue tree generation and caching.
    """
    # If the site repository exists, return the tree.
    if site_repository_exists(app, uri):
        site_repository = SiteRepository(
            uri, branch, app=app, cache=app.config["CACHE"]
        )
        tree = site_repository.get_tree()
        # Save webpage to database
        # Get default owner
        owner = db.session.execute(
            db.select(User).where(User.name == "Default")
        ).scalar()
        # Get default project
        project = db.session.execute(
            db.select(Project).where(Project.name == "Default")
        ).scalar()
        db.session.execute(
            db.insert(Webpage),
            {
                "url": uri,
                "name": uri,
                "owner_id": owner.id,
                "project_id": project.id,
            },
        )
        return tree

    # Return an empty array if the result is not available in 5s.
    p = add_tree_task(uri, branch, app)
    if response := p.join(timeout=5) is None:
        app.logger.info("Task enqueued")
        return []

    return response
