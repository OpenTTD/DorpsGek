import logging

from collections import defaultdict
from dorpsgek.helpers.dorpsgek import get_notification_protocols

log = logging.getLogger(__name__)
_protocols = defaultdict(dict)


async def dispatch(github_api, repository_name, type, payload, ref="master", filter_func=None):
    protocols = await get_notification_protocols(github_api, repository_name, ref, type)

    # If a filter function is set, and it returns False, don't broadcast
    # this notification
    if filter_func:
        if not filter_func(protocols, payload):
            return

    for protocol, userdata in protocols.items():
        # Skip any unknown protocol
        if protocol not in _protocols:
            continue

        try:
            await _protocols[protocol][type](userdata, **payload)
        except Exception:
            log.exception("Protocols callback failed")


def register(name, type):
    def wrapped(func):
        _protocols[name][type] = func
        return func
    return wrapped
