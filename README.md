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

Modify the .env file, and change the following to match your redis instance,

```
REDIS_HOST=your-instance-ip
REDIS_PORT=your-instance-port
```

then load the variables into the shell environment.

```
$ source .env
```

Start the server.

```
$ flask --app webapp/app run --debug
```

## API Requests

#### Getting the website page structure as a JSON tree

<details>
 <summary><code>GET</code> <code><b>/get-tree/site-name</b></code> <code>(gets the entire tree as json)</code></summary>
</details>

<details>
 <summary><code>GET</code> <code><b>/get-tree/site-name/branch-name</b></code> <code>(you can optionally specify the branch)</code></summary>
</details>

```json
{
  "name": "site-name",
  "templates": {
    "children": [
      {
        "children": [
          {
            "children": [],
            "description": "One page",
            "link": null,
            "name": "/blog/article",
            "title": null
          }
        ],
        "description": null,
        "link": "https://docs.google.com/document/d/edit",
        "name": "/blog/",
        "title": null
      }
    ],
    "description": null,
    "link": "https://docs.google.com/document/d//edit",
    "name": "/",
    "title": null
  }
}
```
