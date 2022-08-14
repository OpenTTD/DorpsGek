from ..helpers.github import router
from ..helpers import protocols


@router.register("commit_comment")
async def commit_comment(event, github_api):
    repository_name = event.data["repository"]["full_name"]

    if event.data["action"] != "created":
        return

    commits_url = event.data["repository"]["commits_url"]
    assert commits_url.startswith("https://api.github.com/")
    commits_url = commits_url[len("https://api.github.com") :]
    assert commits_url.endswith("{/sha}")
    commits_url = commits_url.replace("{/sha}", "/" + event.data["comment"]["commit_id"])
    response = await github_api.getitem(commits_url)

    payload = {
        "repository_name": repository_name,
        "url": event.data["comment"]["html_url"],
        "user": event.data["sender"]["login"],
        "avatar_url": event.data["sender"]["avatar_url"],
        "message": response["commit"]["message"].split("\n")[0],
    }

    await protocols.dispatch(github_api, repository_name, "commit-comment", payload)
