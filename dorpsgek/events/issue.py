from dorpsgek.helpers.github import router
from dorpsgek.helpers import protocols


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

    await protocols.dispatch(github_api, repository_name, "issue", payload)


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

    await protocols.dispatch(github_api, repository_name, "issue", payload)
