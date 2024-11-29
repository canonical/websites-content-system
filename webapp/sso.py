import functools
import os

import flask
from django_openid_auth.teams import TeamsRequest, TeamsResponse
from flask_openid import OpenID

SSO_LOGIN_URL = "https://login.ubuntu.com"
SSO_TEAM = "canonical-webmonkeys"
DISABLE_SSO = os.environ.get("DISABLE_SSO")


def init_sso(app: flask.Flask):
    open_id = OpenID(
        store_factory=lambda: None,
        safe_roots=[],
        extension_responses=[TeamsResponse],
    )

    @app.route("/login", methods=["GET", "POST"])
    @open_id.loginhandler
    def login():
        if "openid" in flask.session:
            return flask.redirect(open_id.get_next_url())

        teams_request = TeamsRequest(query_membership=[SSO_TEAM])
        return open_id.try_login(
            SSO_LOGIN_URL, ask_for=["email"], extensions=[teams_request]
        )

    @open_id.after_login
    def after_login(resp):
        if SSO_TEAM not in resp.extensions["lp"].is_member:
            flask.abort(403)

        flask.session["openid"] = {
            "identity_url": resp.identity_url,
            "email": resp.email,
        }

        return flask.redirect(open_id.get_next_url())

    @app.route("/logout")
    def logout():
        if "openid" in flask.session and flask.request.path == "/logout":
            flask.session.pop("openid")

        return flask.redirect("/")

    # Allow CORS
    @app.after_request
    def after_request_func(response):
        response.headers["Access-Control-Allow-Origin"] = SSO_LOGIN_URL
        return response


def login_required(func):
    """
    Decorator that checks if a user is logged in, and redirects
    to login page if not.
    """

    @functools.wraps(func)
    def is_user_logged_in(*args, **kwargs):
        # Return if the sso is explicitly disabled.
        # Useful for non interactive testing.
        if DISABLE_SSO:
            flask.current_app.logger.info(
                "SSO Disabled. Session has no openid."
            )
            return func(*args, **kwargs)

        if "openid" in flask.session:
            return func(*args, **kwargs)

        return flask.redirect("/login?next=" + flask.request.path)

    return is_user_logged_in
