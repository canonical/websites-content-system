import redis


class Redis:
    def __init__(self, app):
        self.host = app.config["REDIS_HOST"]
        self.port = app.config["REDIS_PORT"]

    def connect(self):
        return redis.Redis(host=self.host, port=self.port, db=0)

    def get(self, key):
        return self.connect().get(key)

    def set(self, key, value):
        return self.connect().set(key, value)

    def delete(self, key):
        return self.connect().delete(key)

    def is_available(self):
        try:
            self.connect().ping()
            return True
        except redis.exceptions.ConnectionError:
            return False
        except Exception as e:
            raise e
