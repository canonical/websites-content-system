import queue
import time
from multiprocessing import Process, Queue

import yaml

from webapp.site_repository import SiteRepository, SiteRepositoryError


def init_tasks(app, cache):
    """
    Start event loop.
    """
    background_queue = Queue()
    Process(
        target=load_site_trees,
        args=(app, cache, background_queue),
    ).start()


def load_site_trees(app, cache, queue):
    """
    Load the site trees from the queue.
    """
    while True:
        with open(app.config["BASE_DIR"] + "/" + "sites.yaml") as f:
            data = yaml.safe_load(f)
            for site in data["sites"]:
                Process(
                    target=load_tree_object_async,
                    args=(site, "main", app, cache, queue),
                ).start()
        # Wait for 30 minutes before enqueuing the next set of trees
        time.sleep(1800)


def load_tree_object_async(uri, branch, app, cache, queue=None):
    """
    Put the tree object in the queue.
    """
    app.logger.info(f"Loading {uri}")
    try:
        site_repository = SiteRepository(uri, branch, app=app, cache=cache)
        queue.put(site_repository.get_tree())
    except SiteRepositoryError as e:
        app.logger.error(f"Error loading {uri}: {e}")


def get_tree_async(uri, branch, app, cache):
    """
    Async process to enqueue tree generation and caching.
    """
    task_queue = Queue()
    p = Process(
        target=load_tree_object_async,
        args=(uri, branch, app, cache, task_queue),
    )
    p.start()

    # Try to get the tree from the cache early, return empty array if not 
    # available yet.
    try:
        return task_queue.get(timeout=5)
    except queue.Empty:
        app.logger.info("Task enqueued")

    return []
