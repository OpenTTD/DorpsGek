import base64
import gidgethub
import logging
import yaml

from collections import defaultdict

from .github import get_oauth_token

log = logging.getLogger(__name__)


async def get_dorpsgek_yml(github_api, repository):
    try:
        oauth_token = await get_oauth_token(repository)
        # Always use .dorpsgek.yml from master
        response = await github_api.getitem(
            f"/repos/{repository}/contents/.dorpsgek.yml?ref=master",
            oauth_token=oauth_token,
        )
    except gidgethub.BadRequest as err:
        # Check if there simply wasn't any .dorpsgek.yml in this repository
        if err.args == ("Not Found",):
            return None

        raise

    return base64.b64decode(response["content"])


async def get_notification_protocols(github_api, repository_name, ref, type):
    protocols = defaultdict(list)
    # Always inform the #dorpsgek IRC channel about everything
    protocols["irc"].append("dorpsgek")

    try:
        raw_yml = await get_dorpsgek_yml(github_api, repository_name)
    except Exception:
        log.exception("Couldn't parse .dorpsgek.yml in %s at ref %s", repository_name, ref)
        return protocols

    if not raw_yml:
        return protocols

    yml = yaml.safe_load(raw_yml)

    # If this notification is not enable, don't send any
    if type not in yml["notifications"]:
        return protocols

    # The global list is true for every type
    if "global" in yml["notifications"]:
        for protocol, userdata in yml["notifications"]["global"].items():
            protocols[protocol].extend(userdata)

    # If the type as any specific list, add it too
    if yml["notifications"][type]:
        for protocol, userdata in yml["notifications"][type].items():
            protocols[protocol].extend(userdata)

    return protocols
