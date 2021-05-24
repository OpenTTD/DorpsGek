import re

from ..helpers import protocols
from ..helpers.github import router


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
            # Check for every 'except' if we hit the branch
            for filter in userdata:
                if re.match(filter, payload["branch"]):
                    # If we hit the except, don't notify about this
                    return False

        if protocol == "only":
            # Check for every 'only' if we hit the branch
            for filter in userdata:
                if re.match(filter, payload["branch"]):
                    break
            else:
                # If no 'only' hit, don't notify about this
                return False

    return True


@router.register("push")
async def push(event, github_api):
    # We don't announce created or deleted branches
    if event.data["created"] or event.data["deleted"]:
        return

    branch = event.data["ref"]
    repository_name = event.data["repository"]["full_name"]

    commits = [
        {
            "message": commit["message"].split("\n")[0],
            # Not always the 'username' is set; in those cases, fall back to 'name'
            "author": commit["author"].get("username", commit["author"]["name"]),
        }
        for commit in event.data["commits"]
    ]
    user = event.data["sender"]["login"]

    if len(event.data["commits"]) > 1:
        url = event.data["compare"]
    else:
        url = event.data["commits"][0]["url"]

    # Only notify about pushes to heads; not to tags etc
    if not branch.startswith("refs/heads/"):
        return

    branch = branch[len("refs/heads/") :]

    payload = {
        "repository_name": repository_name,
        "user": user,
        "url": url,
        "branch": branch,
        "commits": commits,
    }

    await protocols.dispatch(github_api, repository_name, "push", payload, filter_func=filter_func)
