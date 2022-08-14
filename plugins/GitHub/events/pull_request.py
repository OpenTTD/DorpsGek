import re

from ..helpers import protocols
from ..helpers.github import router


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

    return True


@router.register("pull_request")
async def pull_request(event, github_api):
    if event.data["action"] not in ("opened", "synchronize", "closed", "reopened"):
        return

    repository_name = event.data["repository"]["full_name"]

    payload = {
        "action": event.data["action"],
        "repository_name": repository_name,
        "pull_id": event.data["pull_request"]["number"],
        "title": event.data["pull_request"]["title"],
        "url": event.data["pull_request"]["html_url"],
        "user": event.data["sender"]["login"],
        "avatar_url": event.data["sender"]["avatar_url"],
        "author": event.data["pull_request"]["user"]["login"],
    }

    if payload["action"] == "closed" and event.data["pull_request"]["merged"]:
        payload["action"] = "merged"

    await protocols.dispatch(github_api, repository_name, "pull-request", payload, filter_func=filter_func)


@router.register("issue_comment")
async def issue_comment(event, github_api):
    if "pull_request" not in event.data["issue"]:
        return

    if event.data["action"] != "created":
        return

    repository_name = event.data["repository"]["full_name"]

    payload = {
        "repository_name": repository_name,
        "pull_id": event.data["issue"]["number"],
        "url": event.data["comment"]["html_url"],
        "user": event.data["sender"]["login"],
        "avatar_url": event.data["sender"]["avatar_url"],
        "title": event.data["issue"]["title"],
        "action": "comment",
        "author": event.data["issue"]["user"]["login"],
    }

    await protocols.dispatch(github_api, repository_name, "pull-request", payload, filter_func=filter_func)


@router.register("pull_request_review")
async def pull_request_review(event, github_api):
    repository_name = event.data["repository"]["full_name"]

    payload = {
        "repository_name": repository_name,
        "pull_id": event.data["pull_request"]["number"],
        "title": event.data["pull_request"]["title"],
        "url": event.data["review"]["html_url"],
        "user": event.data["sender"]["login"],
        "avatar_url": event.data["sender"]["avatar_url"],
        "action": event.data["action"],
        "author": event.data["pull_request"]["user"]["login"],
    }

    if payload["action"] == "submitted":
        payload["action"] = event.data["review"]["state"]

    if payload["action"] not in (
        "dismissed",
        "approved",
        "commented",
        "changes_requested",
    ):
        return

    await protocols.dispatch(github_api, repository_name, "pull-request", payload, filter_func=filter_func)
