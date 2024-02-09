import pyyaml
from webapp.redis import Redis

from webapp.site_repository import SiteRepository


class ParserTask:
    """
    Class to run repository tasks
    """

    def __init__(self, app):
        self.load_repositories()
        self.run_parser()
        self.app = app
        self.redis = Redis(app)

    def __run_in_loop__(self, func, interval=30):
        """
        Run a function in a loop, with a delay between runs
        """

        def wrapper(func, *args, **kwargs):
            while True:
                func(*args, **kwargs)
                time.sleep(interval)

        return wrapper

    def run_parser(self):
        """
        Parse each repository, and save a tree of the templates
        """

        def fn():
            for repo in self.repositories:
                site_repository = SiteRepository(repo, app=self.app)
                tree = site_repository.parse_templates()
                self.save_tree(repo, tree)

        self.__run_in_loop__(fn, interval=60)()

    def load_repositories(self):
        """
        Load pre-configured repositories
        """
        with open("sites.yaml", "r") as f:
            sites_list = pyyaml.load(f)["sites"]
            repo_org = self.app.config["REPO_ORG"]
            self.repositories = [f"{repo_url}/{site}" for site in sites_list]

    def save_tree(self, key, data, branch="main"):
        """
        Save the templates tree data to a file
        """
        # Merge the data with the existing data
        if old_key := self.redis.get(key):
            self.redis.set(
                key,
                {
                    **old_key,
                    branch: data,
                },
            )
        else:
            self.redis.set(
                key,
                {
                    branch: data,
                },
            )
