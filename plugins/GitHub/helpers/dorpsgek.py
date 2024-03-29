import base64
import gidgethub
import logging
import yaml

from collections import defaultdict

from .github import get_oauth_token
from .. import settings

log = logging.getLogger(__name__)


async def get_dorpsgek_yml(github_api, repository):
    try:
        oauth_token = await get_oauth_token(repository)
        # Always use .dorpsgek.yml from the default branch
        response = await github_api.getitem(
            f"/repos/{repository}/contents/.dorpsgek.yml",
            oauth_token=oauth_token,
        )
    except gidgethub.BadRequest as err:
        # Check if there simply wasn't any .dorpsgek.yml in this repository
        if err.args == ("Not Found",):
            return None

        raise

    return base64.b64decode(response["content"])


async def get_notification_protocols(github_api, repository_name, type):
    protocols = defaultdict(list)
    # Always inform the #dorpsgek IRC channel and configured Discord channel about everything
    protocols["irc"].append("dorpsgek")
    if settings.DISCORD_UNFILTERED_WEBHOOK_URL:
        protocols["discord"].append(settings.DISCORD_UNFILTERED_WEBHOOK_URL)

    try:
        raw_yml = await get_dorpsgek_yml(github_api, repository_name)
    except Exception:
        log.exception("Couldn't parse .dorpsgek.yml in %s", repository_name)
        return protocols

    if not raw_yml:
        return protocols

    yml = yaml.safe_load(raw_yml)

    # If this notification is not enable, don't send any
    if type not in yml["notifications"]:
        return protocols

    # For all enabled notification types, also inform Discord
    if settings.DISCORD_WEBHOOK_URL:
        protocols["discord"].append(settings.DISCORD_WEBHOOK_URL)

    # The global list is true for every type
    if "global" in yml["notifications"]:
        for protocol, userdata in yml["notifications"]["global"].items():
            protocols[protocol].extend(userdata)

    # If the type as any specific list, add it too
    if yml["notifications"][type]:
        for protocol, userdata in yml["notifications"][type].items():
            protocols[protocol].extend(userdata)

    return protocols
