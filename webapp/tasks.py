import time
from multiprocessing import Lock, Process, Queue

import yaml
from flask import Flask

from webapp.site_repository import SiteRepository

# Crate the task queue
TASK_QUEUE = Queue()
# Create the locks for the site trees
LOCKS = {}

def init_tasks(app: Flask):
    """
    Start background tasks.
    """

    # @app.before_request
    def start_tasks():
        # Only run once
        app.before_request_funcs[None].remove(start_tasks)

        # Create locks for the preset site trees
        add_site_locks(LOCKS)

        # Start the event loop
        Process(
            target=execute_tasks_in_queue,
            args=(TASK_QUEUE,),
        ).start()

        # Load site trees every 30 minutes
        Process(
            target=load_site_trees,
            args=(app, TASK_QUEUE, LOCKS),
        ).start()

def add_site_locks(locks: dict):
    """
    Create locks for the site trees. These are used to prevent
    multiple threads from trying to update the same repository
    at the same time.
    """
    with open("sites.yaml") as f:
        data = yaml.safe_load(f)
        for site in data["sites"]:
            locks[site] = Lock()
    return locks


def execute_tasks_in_queue(queue: Queue):
    """
    Start the event loop.
    """
    while True:
        if queue.get():
            break


def load_site_trees(app: Flask, queue: Queue, task_locks: dict):
    """
    Load the site trees from the queue.
    """
    while True:
        with open(app.config["BASE_DIR"] + "/" + "sites.yaml") as f:
            data = yaml.safe_load(f)
            for site in data["sites"]:
                # Enqueue the sites for setup
                queue.put_nowait(
                    SiteRepository(
                        site, app, branch="main", task_locks=task_locks
                    )
                )
        # Wait for 30 minutes before enqueuing the next set of trees
        time.sleep(1800)
