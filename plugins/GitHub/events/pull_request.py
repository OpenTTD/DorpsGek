from ..helpers import protocols
from ..helpers.github import router


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
    }

    if payload["action"] == "closed" and event.data["pull_request"]["merged"]:
        payload["action"] = "merged"

    ref = event.data["pull_request"]["base"]["ref"]
    await protocols.dispatch(github_api, repository_name, "pull-request", payload, ref=ref)


@router.register("issue_comment")
async def issue_comment(event, github_api):
    if "pull_request" not in event.data["issue"]:
        return

    if event.data["action"] != "created":
        return

    repository_name = event.data["repository"]["full_name"]

    # To not assume Pull Request are always against 'master',
    # we take an extra roundtrip to find the base branch
    pull_request_url = event.data["issue"]["pull_request"]["url"]
    assert pull_request_url.startswith("https://api.github.com/")
    pull_request_url = pull_request_url[len("https://api.github.com") :]
    response = await github_api.getitem(pull_request_url)

    payload = {
        "repository_name": repository_name,
        "pull_id": event.data["issue"]["number"],
        "url": event.data["comment"]["html_url"],
        "user": event.data["sender"]["login"],
        "title": response["title"],
        "action": "comment",
    }

    ref = response["base"]["ref"]
    await protocols.dispatch(github_api, repository_name, "pull-request", payload, ref=ref)


@router.register("pull_request_review")
async def pull_request_review(event, github_api):
    repository_name = event.data["repository"]["full_name"]

    payload = {
        "repository_name": repository_name,
        "pull_id": event.data["pull_request"]["number"],
        "title": event.data["pull_request"]["title"],
        "url": event.data["review"]["html_url"],
        "user": event.data["sender"]["login"],
        "action": event.data["action"],
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

    ref = event.data["pull_request"]["base"]["ref"]
    await protocols.dispatch(github_api, repository_name, "pull-request", payload, ref=ref)
