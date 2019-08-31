import click
import logging

from aiohttp import web
from dorpsgek import web_routes
from dorpsgek.helpers import (
    github,
    sentry,
)

# Import files that will hook themself up when imported
from dorpsgek.events import (  # noqa
    issue,
    pull_request,
    push,
)
from dorpsgek.patches import gidgethub  # noqa
from dorpsgek.protocols import irc  # noqa

log = logging.getLogger(__name__)

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"]
}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("--github-app-id", help="GitHub App ID")
@click.option("--github-app-private-key", help="GitHub App Private Key", type=click.Path(exists=True, dir_okay=False))
@click.option("--github-app-secret", help="GitHub App Secret", required=True)
@click.option("--port", help="Port of the server", default=80, show_default=True)
@click.option("--sentry-dsn", help="Sentry DSN")
def main(github_app_id, github_app_private_key, github_app_secret, port, sentry_dsn):
    sentry.setup_sentry(sentry_dsn)

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO)

    github.GITHUB_APP_SECRET = github_app_secret
    github.GITHUB_APP_ID = github_app_id
    if github_app_private_key:
        with open(github_app_private_key, "rb") as fp:
            github.GITHUB_APP_PRIVATE_KEY = fp.read()

    irc.startup()

    app = web.Application()
    app.add_routes(web_routes.routes)
    web.run_app(app, port=port)


if __name__ == "__main__":
    main(auto_envvar_prefix='DORPSGEK')
