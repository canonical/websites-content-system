# Template parser backend

Backend service for the CMS template parser

## Getting it running
### Using docker
You'll need to install [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/).

Once done, run:
```
$ docker compose up
```

### Running Locally
You'll need to set up a [redis](https://redis.io/docs/install/install-redis/) server, and expose the port it runs on.

Then install the dependencies.
```bash
$ python -m pip install -r requirements.txt
```

Modify the .env file (if required)

Start the server.
```
$ flask --app webapp/app run --debug
```
