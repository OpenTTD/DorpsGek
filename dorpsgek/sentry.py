import logging
import os
import sentry_sdk

log = logging.getLogger(__name__)


def setup_sentry(sentry_dsn):
    if not sentry_dsn:
        return

    # Release is expected to be in the file '.version'
    with open(".version") as f:
        release = f.readline().strip()
    # HOSTNAME is expected to be in form of 'environment-...'
    environment = os.getenv("HOSTNAME", "dev").split("-")[0]

    sentry_sdk.init(
        sentry_dsn,
        release=release,
        environment=environment)
    log.info("Sentry initialized with release='%s' and environment='%s'", release, environment)
