import time
from multiprocessing import Process

import yaml

from webapp.site_repository import (
    SiteRepository,
    SiteRepositoryError,
    site_repository_exists,
)

# Keep track of generation tasks for each tree.
TREE_TASKS = {}

def init_tasks(app, cache):
    """
    Start event loop.
    """
    Process(
        target=load_site_trees,
        args=(app, cache),
    ).start()


def load_site_trees(app, cache):
    """
    Load the site trees from the queue.
    """
    while True:
        with open(app.config["BASE_DIR"] + "/" + "sites.yaml") as f:
            data = yaml.safe_load(f)
            for site in data["sites"]:
                add_tree_task(site, "main", app, cache)
        # Wait for 30 minutes before enqueuing the next set of trees
        time.sleep(1800)


def add_tree_task(uri, branch, app, cache):
    """
    Put the tree object in the queue.
    """
    # If the tree is already being loaded, return the process.
    if p := TREE_TASKS.get(uri):
        return p

    app.logger.info(f"Loading {uri}")

    def load_tree():
        try:
            site_repository = SiteRepository(uri, branch, app=app, cache=cache)
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


def get_tree_async(uri, branch, app, cache):
    """
    Async process to enqueue tree generation and caching.
    """
    # If the site repository exists, return the tree.
    if site_repository_exists(app, uri):
        site_repository = SiteRepository(uri, branch, app=app, cache=cache)
        return site_repository.get_tree()

    # Return an empty array if the result is not available in 5s.
    p = add_tree_task(uri, branch, app, cache)
    if response := p.join(timeout=5) is None:
        app.logger.info("Task enqueued")
        return []

    return response
