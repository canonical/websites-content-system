import queue
from multiprocessing import Process, Queue

from webapp.site_repository import SiteRepository, SiteRepositoryError


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
