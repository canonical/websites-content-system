import inspect
from multiprocessing import Process, Queue
from typing import Callable

from flask import Flask


def enqueue_task(
    func: Callable, app: Flask, queue: Queue, task_locks: dict, *args, **kwargs
):
    """
    Start the task in a separate process.
    """
    # func must take app, task queue, and locks as arguments
    frame = inspect.currentframe()
    _, _, _, values = inspect.getargvalues(frame)
    for i in ["app", "queue", "task_locks"]:
        if i not in values:
            raise ValueError(
                "Function must take app, task queue, and locks as arguments"
            )

    Process(
        target=func, args=(app, queue, task_locks, *args), kwargs=kwargs
    ).start()
