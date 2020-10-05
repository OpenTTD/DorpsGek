import base64
import click
import logging

from aiohttp import web
from aiohttp.web_log import AccessLogger
from openttd_helpers import click_helper
from openttd_helpers.logging_helper import click_logging
from openttd_helpers.sentry_helper import click_sentry

from dorpsgek import web_routes
from dorpsgek.helpers import github

# Import files that will hook themself up when imported
from dorpsgek.events import (  # noqa
    commit_comment,
    issue,
    pull_request,
    push,
    tag,
)
from dorpsgek.patches import gidgethub  # noqa
from dorpsgek.protocols import irc  # noqa

log = logging.getLogger(__name__)


class ErrorOnlyAccessLogger(AccessLogger):
    def log(self, request, response, time):
        # Only log if the status was not successful
        if not (200 <= response.status < 400):
            super().log(request, response, time)


@click_helper.command()
@click_logging  # Should always be on top, as it initializes the logging
@click_sentry
@click.option("--github-app-id", help="GitHub App ID")
@click.option("--github-app-private-key", help="GitHub App Private Key")
@click.option(
    "--github-app-private-key-file",
    help="GitHub App Private Key",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option("--github-app-secret", help="GitHub App Secret", required=True)
@click.option("--port", help="Port of the server", default=80, show_default=True)
def main(
    github_app_id,
    github_app_private_key,
    github_app_private_key_file,
    github_app_secret,
    port,
):
    github.GITHUB_APP_SECRET = github_app_secret
    github.GITHUB_APP_ID = github_app_id
    if github_app_private_key_file:
        with open(github_app_private_key_file, "rb") as fp:
            github.GITHUB_APP_PRIVATE_KEY = fp.read()
    if github_app_private_key:
        github.GITHUB_APP_PRIVATE_KEY = base64.b64decode(github_app_private_key)

    irc.startup()

    app = web.Application()
    app.add_routes(web_routes.routes)
    web.run_app(app, port=port, access_log_class=ErrorOnlyAccessLogger)


if __name__ == "__main__":
    main(auto_envvar_prefix="DORPSGEK")
