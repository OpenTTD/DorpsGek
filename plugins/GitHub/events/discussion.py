from ..helpers.github import router
from ..helpers import protocols


@router.register("discussion")
async def discussion(event, github_api):
    repository_name = event.data["repository"]["full_name"]

    payload = {
        "action": event.data["action"],
        "repository_name": repository_name,
        "discussion_id": event.data["discussion"]["number"],
        "title": event.data["discussion"]["title"],
        "url": event.data["discussion"]["html_url"],
        "user": event.data["sender"]["login"],
    }

    if payload["action"] not in ("created",):
        return

    await protocols.dispatch(github_api, repository_name, "discussion", payload)


@router.register("discussion_comment")
async def discussion_comment(event, github_api):
    if event.data["action"] != "created":
        return

    repository_name = event.data["repository"]["full_name"]

    payload = {
        "action": "comment",
        "repository_name": repository_name,
        "discussion_id": event.data["discussion"]["number"],
        "title": event.data["discussion"]["title"],
        "url": event.data["discussion"]["html_url"],
        "user": event.data["sender"]["login"],
    }

    await protocols.dispatch(github_api, repository_name, "discussion", payload)
