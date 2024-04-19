import time
import yaml
from multiprocess import Process

from webapp.site_repository import SiteRepository, SiteRepositoryError


def worker(func, interval):
    while True:
        time.sleep(interval)
        func()


class ParserTask:
    """
    Class to run repository tasks
    """

    def __init__(self, app, cache):
        self.app = app
        self.cache = cache
        self.start_worker()

    def __worker_loop__(self, func, interval=30):
        """
        Run a detached function in a loop, with a delay between runs
        """

        self.app.logger.info(f"Starting worker for {func.__name__}")
        thread = Process(target=worker, args=(func, interval))
        thread.start()

    def start_worker(self):
        """
        Initialize each repository on a 60s loop
        """
        self.__worker_loop__(self.load_repositories, 60)

    def load_repositories(self):
        """
        Load pre-configured repositories
        """
        with open("sites.yaml", "r") as f:
            sites_list = yaml.safe_load(f)["sites"]
            for site in sites_list:
                self.app.logger.info(f"Loading {site}")
                try:
                    site_repository = SiteRepository(
                        site, app=self.app, cache=self.cache
                    )
                    site_repository.get_tree()
                except SiteRepositoryError as e:
                    self.app.logger.error(f"Error loading {site}: {e}")
                    continue
