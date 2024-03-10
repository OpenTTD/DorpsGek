import re

from ..helpers.github import router
from ..helpers import protocols


def filter_func(protocols, payload):
    # Filter based on some keywords
    for protocol, userdata in protocols.items():
        if protocol == "except-by":
            # Check for every 'except' if we hit the user
            for filter in userdata:
                if re.match(filter, payload["author"]):
                    # If we hit the except, don't notify about this
                    return False

        if protocol == "only-by":
            # Check for every 'only' if we hit the user
            for filter in userdata:
                if re.match(filter, payload["author"]):
                    break
            else:
                # If no 'only' hit, don't notify about this
                return False

        if protocol == "except":
            # Check for every 'except' if we hit the path
            for filter in userdata:
                if re.match(filter, payload["path"]):
                    # If we hit the except, don't notify about this
                    return False

        if protocol == "only":
            # Check for every 'only' if we hit the path
            for filter in userdata:
                if re.match(filter, payload["path"]):
                    break
            else:
                # If no 'only' hit, don't notify about this
                return False

    return True


@router.register("workflow_run")
async def workflow_run(event, github_api):
    repository_name = event.data["repository"]["full_name"]

    if event.data["action"] != "completed":
        return

    payload = {
        "repository_name": repository_name,
        "url": event.data["workflow_run"]["html_url"],
        "user": event.data["sender"]["login"],
        "avatar_url": event.data["sender"]["avatar_url"],
        "workflow_name": event.data["workflow_run"]["name"],
        "conclusion": event.data["workflow_run"]["conclusion"],
        "author": event.data["workflow_run"]["actor"]["login"],
        "path": event.data["workflow_run"]["path"],
    }

    await protocols.dispatch(github_api, repository_name, "workflow-run", payload, filter_func=filter_func)
