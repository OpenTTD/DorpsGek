from ..helpers.github import router
from ..helpers import protocols


@router.register("create")
async def create(event, github_api):
    repository_name = event.data["repository"]["full_name"]
    repository_url = event.data["repository"]["html_url"]

    ref_name = event.data["ref"]
    ref_type = event.data["ref_type"]
    if ref_type == "branch":
        url = f"{repository_url}/tree/{ref_name}"
    elif ref_type == "tag":
        url = f"{repository_url}/releases/tag/{ref_name}"
    else:
        return  # Shouldn't happen

    payload = {
        "repository_name": repository_name,
        "user": event.data["sender"]["login"],
        "url": url,
        "name": ref_name,
    }
    await protocols.dispatch(github_api, repository_name, f"{ref_type}-created", payload)
