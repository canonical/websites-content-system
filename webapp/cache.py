import json
import os
import shutil
from pathlib import Path

import valkey


def init_cache(app):
    try:
        cache = ValkeyCache(app)
    except ConnectionError as e:
        app.logger.info(
            e, "Valkey cache is not available. Using FileCache instead."
        )
        cache = FileCache(app)
    return cache


class ValkeyCache:
    """Cache interface"""

    CACHE_PREFIX = "WEBSITES-CONTENT-SYSTEM"

    def __init__(self, app):
        self.host = app.config["VALKEY_HOST"]
        self.port = app.config["VALKEY_PORT"]
        self.logger = app.logger
        self.instance = self.connect()

    def connect(self):
        """
        Return an instance of the valkey cache. If not available, throw a
        ConnectionError.
        """
        self.logger.info(
            f"Connecting to Valkey cache at {self.host}:{self.port}"
        )
        try:
            r = valkey.Valkey(host=self.host, port=self.port, db=0)
            r.ping()
            return r
        except (
            valkey.exceptions.ConnectionError,
            valkey.exceptions.TimeoutError,
        ):
            raise ConnectionError("Valkey cache is not available")

    def __get_prefixed_key__(self, key):
        return f"{self.CACHE_PREFIX}_{key}"

    def get(self, key):
        return self.instance.get(self.__get_prefixed_key__(key))

    def set(self, key, value):
        return self.instance.set(self.__get_prefixed_key__(key), value)

    def delete(self, key):
        return self.instance.delete(key)

    def is_available(self):
        try:
            self.instance.ping()
            return True
        except valkey.exceptions.ConnectionError:
            return False
        except Exception as e:
            raise e


class FileCacheError(Exception):
    """
    Exception raised for errors in the FileCache class.
    """


class FileCache:
    """Cache interface"""

    CACHE_DIR = "tree-cache"
    CACHE_PREFIX = "WEBSITES_CONTENT_SYSTEM"

    def __init__(self, app):
        self.cache_path = app.config["BASE_DIR"] + "/" + self.CACHE_DIR
        self.logger = app.logger
        # Create directory
        Path(self.cache_path).mkdir(parents=True, exist_ok=True)
        self.connect()

    def connect(self):
        """
        Check if the cache directory exists, and is writable.
        """
        self.logger.info(f"Connecting to FileCache at {self.cache_path}")

        path_exists = Path(self.cache_path).exists()
        path_writable = Path(self.cache_path).is_dir() and os.access(
            self.cache_path, os.W_OK
        )
        if not path_exists and path_writable:
            raise ConnectionError("Cache directory is not writable")

    def save_to_file(self, key, value):
        """
        Dump the python object to JSON and save it to a file.
        """
        data = json.dumps(value)
        # Delete the file if it exists
        if Path(self.cache_path + "/" + key).exists():
            os.remove(self.cache_path + "/" + key)
        with open(self.cache_path + "/" + key, "w") as f:
            f.write(data)

    def load_from_file(self, key):
        """
        Load the JSON data from a file and return the python object.
        """
        # Check if the file exists
        if not Path(self.cache_path + "/" + key).exists():
            return None
        with open(self.cache_path + "/" + key, "r") as f:
            data = f.read()
        return json.loads(data)

    def __get_prefixed_key__(self, key):
        return f"{self.CACHE_PREFIX}_{key}"

    def get(self, key):
        return self.load_from_file(self.__get_prefixed_key__(key))

    def set(self, key, value):
        return self.save_to_file(self.__get_prefixed_key__(key), value)

    def delete(self, key):
        """
        Delete the file from the cache directory.
        """

        def onerror(*args, **kwargs):
            os.chmod(self.cache_path + "/" + key, 0o777)

        return shutil.rmtree(self.cache_path + "/" + key, onerror=onerror)
