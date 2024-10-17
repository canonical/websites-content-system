import functools
import os
import time
from multiprocessing import Lock, Process, Queue

import yaml
from flask import Flask
from flask_sqlalchemy import SQLAlchemy

from webapp.models import db
from webapp.site_repository import SiteRepository

# Crate the task queue
TASK_QUEUE = Queue()
# Create the locks for the site trees
LOCKS = {}
# Default delay between runs for scheduled tasks
TASK_DELAY = int(os.getenv("TASK_DELAY", 5))


def init_tasks(app: Flask):
    """
    Start background tasks.
    """

    @app.before_request
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

        # Load site trees
        Process(
            target=load_site_trees,
            args=(app, db, TASK_QUEUE, LOCKS),
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


def scheduled_task(delay=30):
    """
    Wrapper for long running tasks, with an optional delay between runs.
    """

    def outerwrapper(func, delay=delay):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            while True:
                func(*args, **kwargs)
                time.sleep(delay * 60)

        return wrapper

    return outerwrapper


@scheduled_task(delay=1)
def execute_tasks_in_queue(queue: Queue):
    """
    Start the event loop.
    """
    queue.get()


@scheduled_task(delay=TASK_DELAY)
def load_site_trees(
    app: Flask, database: SQLAlchemy, queue: Queue, task_locks: dict
):
    """
    Load the site trees from the queue.
    """
    app.logger.info("Running scheduled task: load_site_trees")
    with open(app.config["BASE_DIR"] + "/" + "sites.yaml") as f:
        data = yaml.safe_load(f)
        for site in data["sites"]:
            # Enqueue the sites for setup
            site_repository = SiteRepository(
                site, app, db=database, task_locks=task_locks
            )
            # build the tree from GH source without using cache
            queue.put(site_repository.get_tree(True))
