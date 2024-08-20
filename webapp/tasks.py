import functools
import time
from multiprocessing import Lock, Process, Queue

import yaml
from flask import Flask
from sqlalchemy import delete, select

from webapp.models import Webpage, WebpageStatus, db
from webapp.site_repository import SiteRepository

# Crate the task queue
TASK_QUEUE = Queue()
# Create the locks for the site trees
LOCKS = {}


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

        # Load site trees every 30 minutes
        Process(
            target=load_site_trees,
            args=(app, TASK_QUEUE, LOCKS),
        ).start()

        # Update webpages every 30 minutes
        Process(
            target=update_deleted_webpages,
            args=(app, TASK_QUEUE, LOCKS),
        ).start()

        Process(
            target=update_new_webpages,
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


@scheduled_task(delay=30)
def load_site_trees(app: Flask, queue: Queue, task_locks: dict):
    """
    Load the site trees from the queue.
    """
    app.logger.info("Running scheduled task: load_site_trees")
    with open(app.config["BASE_DIR"] + "/" + "sites.yaml") as f:
        data = yaml.safe_load(f)
        for site in data["sites"]:
            # Enqueue the sites for setup
            queue.put_nowait(SiteRepository(site, app, task_locks=task_locks))


@scheduled_task(delay=30)
def update_deleted_webpages(app: Flask, queue: Queue, task_locks: dict):
    """
    Webpages that have TO_DELETE status and do not exist in the parsed tree
    structure will be deleted.
    """
    app.logger.info("Running scheduled task: update_deleted_webpages")
    webpages_to_delete = db.session.execute(
        select(Webpage).where(Webpage.status == WebpageStatus.TO_DELETE)
    )

    for row in webpages_to_delete:
        webpage = row[0]
        site_repository = SiteRepository(
            webpage.project.name, app, task_locks=task_locks
        ).get_new_tree()
        site_webpages = site_repository.get_webpages()
        # Delete if the webpage doesn't exist in the current tree structure
        if webpage.name not in site_webpages:
            queue.put(
                db.session.execute(
                    delete(Webpage).where(Webpage.id == webpage.id)
                )
            )


@scheduled_task(delay=30)
def update_new_webpages(app: Flask, queue: Queue, task_locks: dict):
    """
    Webpages that have NEW status and exist in the parsed tree structure
    will have their status updated to AVAILABLE.
    """
    app.logger.info("Running scheduled task: update_new_webpages")
    new_webpages = db.session.execute(
        select(Webpage).where(Webpage.status == WebpageStatus.NEW)
    )

    for row in new_webpages:
        webpage = row[0]
        site_repository = SiteRepository(
            webpage.project.name, app, task_locks=task_locks
        ).get_tree()
        # Update the status if the webpage exists in the current tree structure
        if webpage.name in site_repository.get_webpages():
            webpage.status = WebpageStatus.AVAILABLE
            db.session.add(webpage)
            queue.put(db.session.commit())
