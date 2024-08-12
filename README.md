# Template parser backend

Backend service for the CMS template parser

## Getting it running

### Environment variables

Before starting, update the environment variables if needed. The default values will work for docker, save the `GH_TOKEN` which must be manually set. You can create a token [here](https://github.com/settings/tokens), by following [these](https://docs.github.com/en/authentication/keeping-your-account-and-data-secure/managing-your-personal-access-tokens) instructions. Make sure to select the `repo` scope for the token.

```env
PORT=8104
FLASK_DEBUG=true
SECRET_KEY=secret_key
DEVEL=True
VALKEY_HOST=0.0.0.0
VALKEY_PORT=6379
GH_TOKEN=ghp_somepersonaltoken
```

### Using docker

You'll need to install [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/).

Once done, run:

```
$ docker compose up
```

### Running Locally

#### Cache
The service depends on having a cache from which generated tree json can be sourced.

You'll need to set up a [valkey](https://valkey.io/) or [redis](https://redis.io/docs/install/install-redis/) cache, and expose the port it runs on.
If you do not want to use a dedicated cache, a simple filecache has been included as the default. Data is saved to the `./tree-cache/` directory. 

First, install the dependencies.

```bash
$ python -m pip install -r requirements.txt
```

Then modify the .env file, and change the following to match your redis instance,

```
VALKEY_HOST=your-instance-ip
VALKEY_PORT=your-instance-port
```

and load the variables into the shell environment.

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
