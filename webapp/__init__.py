import hashlib
import os

import flask
from flask_cors import CORS
from werkzeug.debug import DebuggedApplication
from werkzeug.middleware.proxy_fix import ProxyFix

from webapp.cache import init_cache
from webapp.context import RegexConverter, base_context, clear_trailing_slash
from webapp.gdrive import init_gdrive
from webapp.jira import init_jira
from webapp.models import init_db
from webapp.sso import init_sso
from webapp.tasks import init_tasks


def create_app():
    app = FlaskBase(
        __name__,
        "cs.canonical.com",
        template_folder="../templates",
        static_folder="../static",
    )
    app.config.from_pyfile("settings.py")
    app.context_processor(base_context)

    # Add CORS headers
    CORS(app, origins=["https://login.ubuntu.com"])

    # Initialize database
    init_db(app)

    # Initialize SSO
    init_sso(app)

    # Initialize cache
    init_cache(app)

    # Initialize tasks
    init_tasks(app)

    # Initialize JIRA
    init_jira(app)

    # Initialize gdrive
    init_gdrive(app)

    return app


# Sensible defaults, got from flask base. We do this instead of installing the
# package to avoid dependency conflicts with talisker on python 3.12
# https://github.com/canonical/canonicalwebteam.flask-base/blob/main/canonicalwebteam/flask_base/app.py


def set_security_headers(response):
    # Decide whether to add x-frame-options
    add_xframe_options_header = True

    # Check if view_function has exclude_xframe_options_header decorator
    if flask.request.endpoint in flask.current_app.view_functions:
        view_func = flask.current_app.view_functions[flask.request.endpoint]
        add_xframe_options_header = not hasattr(
            view_func, "_exclude_xframe_options_header"
        )

    if add_xframe_options_header and "X-Frame-Options" not in response.headers:
        response.headers["X-Frame-Options"] = "SAMEORIGIN"

    # Add standard security headers
    response.headers["X-Content-Type-Options"] = "NOSNIFF"

    return response


def set_cache_control_headers(response):
    """
    Default caching rules that should work for most pages
    """

    if flask.request.path.startswith("/_status"):
        # Our status endpoints need to be uncached
        # to report accurate information at all times
        response.cache_control.no_store = True

    elif (
        response.status_code == 200
        and not response.cache_control.no_store
        and not response.cache_control.no_cache
        and not response.cache_control.private
    ):
        # Normal responses, where the cache-control object hasn't
        # been independently modified, should:

        max_age = response.cache_control.max_age
        stale_while_revalidate = response.cache_control._get_cache_value(
            "stale-while-revalidate", False, int
        )
        stale_if_error = response.cache_control._get_cache_value(
            "stale-if-error", False, int
        )

        if type(max_age) is not int:
            # Hard-cache for a minimal amount of time so content can be easily
            # refreshed.
            #
            # The considerations here are as follows:
            # - To avoid caching headaches, it's best if when people need to
            #   refresh a page (e.g. after they've just done a release) they
            #   can do so by simply refreshing their browser.
            # - However, it needs to be long enough to protect our
            #   applications from excessive requests from all the pages being
            #   generated (a factor)
            #
            # 1 minute seems like a good compromise.
            response.cache_control.max_age = "60"

        if type(stale_while_revalidate) is not int:
            # stale-while-revalidate defines a period after the cache has
            # expired (max-age) during which users will get sent the stale
            # cache, while the cache updates in the background. This mean
            # that users will continue to get speedy (potentially stale)
            # responses even if the refreshing of the cache takes a while,
            # but the content should still be no more than a few seconds
            # out of date.
            #
            # We want this to be pretty long, so users will still get a
            # quick response (while triggering a background update) for
            # as long as possible after the cache has expired.
            #
            # An additional day will hopefully be long enough for most cases.
            response.cache_control._set_cache_value(
                "stale-while-revalidate", "86400", int
            )

        if type(stale_if_error) is not int:
            # stale-if-error defines a period of time during which a stale
            # cache will be served back to the client if the cache observes
            # an error code response (>=500) from the backend. When the cache
            # receives a request for an erroring page, after serving the stale
            # page it will ping off a background request to attempt the
            # revalidate the page, as long as it's not currently waiting for a
            # response.
            #
            # We set this value to protect us from transitory errors. The
            # trade-off here is that we may also be masking errors from
            # ourselves. While we have Sentry and Greylog to potentially alert
            # us, we might miss these alerts, which could lead to much more
            # serious issues (e.g. bringing down the whole site). The most
            # clear manifestation of these error would be simply an error on
            # the site.
            #
            # So we set this to 5 minutes following expiry as a trade-off.
            response.cache_control._set_cache_value(
                "stale-if-error", "300", int
            )

    return response


def set_permissions_policy_headers(response):
    """
    Sets default permissions policies. This disable some browsers features
    and APIs.
    """
    # Disabling interest-cohort for privacy reasons.
    # https://wicg.github.io/floc/
    response.headers["Permissions-Policy"] = "interest-cohort=()"

    return response


def set_clacks(response):
    """
    Keep Sir Terry Pratchett's name alive
    https://xclacksoverhead.org/home/about
    """

    response.headers["X-Clacks-Overhead"] = "GNU Terry Pratchett"

    return response


class FlaskBase(flask.Flask):
    def send_static_file(self, filename: str) -> "flask.wrappers.Response":
        """
        Overwrite the default Flask send_static_file method,
        to simply check if the `v=` parameter is provided,
        and if so, return 404 if the expected hash doesn't
        match the contents
        """

        response = super().send_static_file(filename)

        expected_hash = flask.request.args.get("v")

        # File exists, and we have a version has to compare to
        if response.status_code == 200 and expected_hash:
            # Convert this to a non-streaming Response object,
            # so we can inspect the contents
            # https://github.com/closeio/Flask-gzip/issues/7#issuecomment-23373695
            response.direct_passthrough = False

            # Get an md5 hash of the contents
            file_hash = hashlib.md5(response.data).hexdigest()

            # If it matches the expected hash, it should be safe to cache
            # this file for a year, as the contents will never change at this
            # URL
            if file_hash.startswith(expected_hash):
                response.headers["Cache-Control"] = "public, max-age=31536000"

            # If it doesn't match, return 404
            else:
                flask.abort(404)

        # Now return the static file response
        return response

    def __init__(
        self,
        name,
        service,
        favicon_url=None,
        template_404=None,
        template_500=None,
        *args,
        **kwargs,
    ):
        super().__init__(name, *args, **kwargs)

        self.service = service

        self.config["SECRET_KEY"] = os.environ["SECRET_KEY"]

        self.url_map.strict_slashes = False
        self.url_map.converters["regex"] = RegexConverter

        if self.debug:
            self.wsgi_app = DebuggedApplication(self.wsgi_app)

        self.wsgi_app = ProxyFix(self.wsgi_app)

        self.before_request(clear_trailing_slash)

        self.after_request(set_security_headers)
        self.after_request(set_cache_control_headers)
        self.after_request(set_permissions_policy_headers)
        self.after_request(set_clacks)

        self.context_processor(base_context)

        # Default error handlers
        if template_404:

            @self.errorhandler(404)
            def not_found_error(error):
                return (
                    flask.render_template(
                        template_404, message=error.description
                    ),
                    404,
                )

        if template_500:

            @self.errorhandler(500)
            def internal_error(error):
                return (
                    flask.render_template(
                        template_500, message=error.description
                    ),
                    500,
                )

        # Default routes
        @self.route("/_status/check")
        def status_check():
            return "OK"

        favicon_path = os.path.join(self.root_path, "../static", "favicon.ico")
        if os.path.isfile(favicon_path):

            @self.route("/favicon.ico")
            def favicon():
                return flask.send_file(
                    favicon_path, mimetype="image/vnd.microsoft.icon"
                )

        elif favicon_url:

            @self.route("/favicon.ico")
            def favicon():
                return flask.redirect(favicon_url)

        robots_path = os.path.join(self.root_path, "..", "robots.txt")
        humans_path = os.path.join(self.root_path, "..", "humans.txt")
        security_path = os.path.join(self.root_path, "..", "security.txt")

        if os.path.isfile(robots_path):

            @self.route("/robots.txt")
            def robots():
                return flask.send_file(robots_path)

        if os.path.isfile(humans_path):

            @self.route("/humans.txt")
            def humans():
                return flask.send_file(humans_path)

        if os.path.isfile(security_path):

            @self.route("/.well-known/security.txt")
            def security():
                return flask.send_file(security_path)
