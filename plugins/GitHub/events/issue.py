import re

from ..helpers.github import router
from ..helpers import protocols


def filter_func(protocols, payload):
    # Filter based on some keywords
    for protocol, userdata in protocols.items():
        if protocol == "except-by":
            # Check for every 'except' if we hit the user
            for filter in userdata:
                if re.match(filter, payload["user"]):
                    # If we hit the except, don't notify about this
                    return False

        if protocol == "only-by":
            # Check for every 'only' if we hit the user
            for filter in userdata:
                if re.match(filter, payload["user"]):
                    break
            else:
                # If no 'only' hit, don't notify about this
                return False

        if protocol == "except":
            # Check for every 'except' if we hit the action
            for filter in userdata:
                if re.match(filter, payload["action"]):
                    # If we hit the except, don't notify about this
                    return False

        if protocol == "only":
            # Check for every 'only' if we hit the action
            for filter in userdata:
                if re.match(filter, payload["action"]):
                    break
            else:
                # If no 'only' hit, don't notify about this
                return False

    return True


@router.register("issues")
async def issues(event, github_api):
    repository_name = event.data["repository"]["full_name"]

    payload = {
        "action": event.data["action"],
        "repository_name": repository_name,
        "issue_id": event.data["issue"]["number"],
        "title": event.data["issue"]["title"],
        "url": event.data["issue"]["html_url"],
        "user": event.data["sender"]["login"],
    }

    if payload["action"] not in ("opened", "closed", "reopened"):
        return

    await protocols.dispatch(github_api, repository_name, "issue", payload, filter_func=filter_func)


@router.register("issue_comment")
async def issue_comment(event, github_api):
    if "pull_request" in event.data["issue"]:
        return

    if event.data["action"] != "created":
        return

    repository_name = event.data["repository"]["full_name"]

    payload = {
        "action": "comment",
        "repository_name": repository_name,
        "issue_id": event.data["issue"]["number"],
        "title": event.data["issue"]["title"],
        "url": event.data["issue"]["html_url"],
        "user": event.data["sender"]["login"],
    }

    await protocols.dispatch(github_api, repository_name, "issue", payload, filter_func=filter_func)
