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
REPO_ORG=https://github.com/canonical
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/content
TASK_DELAY=30
DIRECTORY_API_TOKEN=token
JIRA_EMAIL=example@canonical.com
JIRA_TOKEN=jiratoken
JIRA_URL=https://warthogs.atlassian.net
JIRA_LABELS=sites_BAU
JIRA_COPY_UPDATES_EPIC=WD-12643
GOOGLE_SERVICE_ACCOUNT=base64encodedjsonfile
GOOGLE_DRIVE_FOLDER_ID=1EIFOGJ8DIWpsYIfWk7Yos3YijZIkbJDk
COPYD0C_TEMPLATE_ID=125auRsLQukYH-tKN1oEKaksmpCXd_DTGiswvmbeS2iA
```

### Using docker

You'll need to install [docker](https://docs.docker.com/engine/install/) and [docker-compose](https://docs.docker.com/compose/install/).

Once done, run:

```
$ docker compose up
```

### Running Locally

#### Cache and Database
The service depends on having a cache from which generated tree json can be sourced, as well as a postgres database.

You'll need to set up a [valkey](https://valkey.io/) or [redis](https://redis.io/docs/install/install-redis/) cache, and expose the port it runs on.
If you do not want to use a dedicated cache, a simple filecache has been included as the default. Data is saved to the `./tree-cache/` directory. 

```bash
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres
docker run -d -p 6379:6379 valkey/valkey
```

First, install the dependencies.

```bash
$ python -m pip install -r requirements.txt
```

Then modify the .env file, and change the following to match your valkey and postgres instances. The config below works for dotrun as well.

```
# .env
VALKEY_HOST=localhost
VALKEY_PORT=5379
SQLALCHEMY_DATABASE_URI=postgresql://postgres:postgres@localhost:5432/postgres
```

and load the variables into the shell environment.

```
$ source .env
```

Start the server.

```
$ flask --app webapp/app run --debug
```

#### Locally, with dotrun
You can optionally use dotrun to start the service. When the 1.1.0-rc1 branch is merged, then we can use dotrun without the `--release` flag.

```
$ dotrun build && dotrun
```

### Note for using dotrun on mac
Since macs don't support host mode on docker, you'll have to get the valkey and postgres ip addresses manually from the running docker containers, and replace the host values in the .env file *before* running dotrun
```bash
$ docker inspect <valkey-container-id> | grep IPAddress
$ docker inspect <postgres-container-id> | grep IPAddress
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

#### Making a webpage update request

<details>
 <summary><code>POST</code> <code><b>/request-changes</b></code>
</details>

```json
{
  "due_date": "2022-01-01",
  "reporter_id": 1,
  "webpage_id": 31,
  "type": 1,
  "description": "This is a description",
}