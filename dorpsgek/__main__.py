import click
import logging

from aiohttp import web
from dorpsgek import sentry, web_routes

log = logging.getLogger(__name__)

CONTEXT_SETTINGS = {
    "help_option_names": ["-h", "--help"]
}


@click.command(context_settings=CONTEXT_SETTINGS)
@click.option("--port", help="Port of the server", default=443, show_default=True)
@click.option("--sentry-dsn", help="Sentry DSN", required=False)
def main(port, sentry_dsn):
    sentry.setup_sentry(sentry_dsn)

    logging.basicConfig(
        format="%(asctime)s %(levelname)-8s %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        level=logging.INFO)

    app = web.Application()
    app.add_routes(web_routes.routes)
    web.run_app(app, port=port)


if __name__ == "__main__":
    main(auto_envvar_prefix='DORPSGEK')
