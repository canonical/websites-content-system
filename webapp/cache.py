import valkey

class Cache:
    """Cache interface"""

    def __init__(self, app):
        self.host = app.config["VALKEY_HOST"]
        self.port = app.config["VALKEY_PORT"]
        self.instance = self.connect()

    def connect(self):
        """
        Return an instance of the redis cache. If not available, throw a
        ConnectionError.
        """
        try:
            r = valkey.Redis(host=self.host, port=self.port, db=0)
            r.ping()
            return r
        except (
            valkey.exceptions.ConnectionError,
            valkey.exceptions.TimeoutError,
        ):
            raise ConnectionError("Redis cache is not available")

    def connect_redis(self):
        return valkey.Redis(host=self.host, port=self.port, db=0)

    def get(self, key):
        return self.instance.get(key)

    def set(self, key, value):
        return self.instance.set(key, value)

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
