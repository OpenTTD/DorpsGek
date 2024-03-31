import aiohttp
import logging

from ..helpers import protocols

log = logging.getLogger(__name__)


async def _send_messages(hook_urls, user, avatar_url, message):
    async with aiohttp.ClientSession() as session:
        for hook_url in hook_urls:
            resp = await session.post(
                hook_url,
                json={
                    "embeds": [
                        {
                            "description": message,
                            "color": 0xFD7605,
                        }
                    ],
                    "username": f"{user} (via GitHub)",
                    "avatar_url": avatar_url,
                    "allowed_mentions": {
                        "parse": [],
                    },
                },
                headers={
                    "User-Agent": "DorpsGek (https://github.com/OpenTTD/DorpsGek, 1.0)",
                },
            )
            if resp.status not in (200, 204):
                log.error(f"Failed to send message to Discord: {resp.status}")


@protocols.register("discord", "pull-request")
async def pull_request(hook_urls, repository_name, url, user, avatar_url, action, pull_id, title, author):
    message = f"**{repository_name}** - "

    if action == "opened":
        message += f":postbox: opened pull request [#{pull_id}]({url})\n> {title}"
    elif action == "closed":
        message += f":no_entry: closed pull request [#{pull_id}]({url})\n> {title}"
    elif action == "merged":
        message += f":rocket: merged pull request [#{pull_id}]({url})\n> {title}"
    elif action == "synchronize":
        message += f":mega: updated pull request [#{pull_id}]({url})\n> {title}"
    elif action == "reopened":
        message += f":mailbox_with_mail: reopened pull request [#{pull_id}]({url})\n> {title}"
    elif action == "comment":
        message += f":speech_balloon: commented on pull request [#{pull_id}]({url})\n> {title}"
    elif action == "dismissed":
        message += f":eyes: dismissed a review for pull request [#{pull_id}]({url})\n> {title}"
    elif action == "approved":
        message += f":thumbsup: approved pull request [#{pull_id}]({url})\n> {title}"
    elif action == "changes_requested":
        message += f":negative_squared_cross_mark: requested changes for pull request [#{pull_id}]({url})\n> {title}"
    elif action == "commented":
        message += f":speech_balloon: commented on pull request [#{pull_id}]({url})\n> {title}"
    else:
        return

    await _send_messages(hook_urls, user, avatar_url, message)


@protocols.register("discord", "push")
async def push(hook_urls, repository_name, url, user, avatar_url, branch, commits):
    if len(commits) == 1:
        commit_text = "a commit"
    else:
        commit_text = f"{len(commits)} commits"

    message = f"**{repository_name}** - :muscle: pushed [{commit_text}]({url}) to `{branch}`\n> "
    message += "\n> ".join([f"{commit['message']} (by {commit['author']})" for commit in commits])

    await _send_messages(hook_urls, user, avatar_url, message)


@protocols.register("discord", "issue")
async def issue(hook_urls, repository_name, url, user, avatar_url, action, issue_id, title, reason):
    message = f"**{repository_name}** - "

    if action == "opened":
        message += f":beetle: opened issue [#{issue_id}]({url})\n> {title}"
    elif action == "reopened":
        message += f":scream_cat: reopened issue [#{issue_id}]({url})\n> {title}"
    elif action == "closed":
        if reason == "completed":
            message += f":sunglasses: closed issue [#{issue_id}]({url})\n> {title}"
        else:
            message += f":triumph: closed issue [#{issue_id}]({url})\n> {title}"
    elif action == "comment":
        message += f":speech_balloon: commented on issue [#{issue_id}]({url})\n> {title}"
    else:
        return

    await _send_messages(hook_urls, user, avatar_url, message)


@protocols.register("discord", "discussion")
async def discussion(hook_urls, repository_name, url, user, avatar_url, action, discussion_id, title):
    message = f"**{repository_name}** - "

    if action == "created":
        message += f":speaking_head: started discussion [#{discussion_id}]({url})\n> {title}"
    elif action == "comment":
        message += f":speech_balloon: commented on discussion [#{discussion_id}]({url})\n> {title}"
    else:
        return

    await _send_messages(hook_urls, user, avatar_url, message)


@protocols.register("discord", "commit-comment")
async def commit_comment(hook_urls, repository_name, url, user, avatar_url, first_line):
    message = f"**{repository_name}** - "
    message += f":open_mouth: left a comment on commit: {url}\n> {first_line}"

    await _send_messages(hook_urls, user, avatar_url, message)


@protocols.register("discord", "branch-created")
async def ref_branch_created(hook_urls, repository_name, url, user, avatar_url, name):
    message = f"**{repository_name}** - "
    message += f":cow: created a new branch [{name}]({url})"

    await _send_messages(hook_urls, user, avatar_url, message)


@protocols.register("discord", "tag-created")
async def ref_tag_created(hook_urls, repository_name, url, user, avatar_url, name):
    message = f"**{repository_name}** - "
    message += f":tada: created a new tag [{name}]({url})"

    await _send_messages(hook_urls, user, avatar_url, message)


@protocols.register("discord", "workflow-run")
async def workflow_run(hook_urls, repository_name, url, user, avatar_url, workflow_name, conclusion, author, path):
    if conclusion in ("success", "skipped"):
        return

    message = f"**{repository_name}** - "
    message += f":thunder_cloud_rain: [{workflow_name}]({url}) workflow was not successful"

    await _send_messages(hook_urls, user, avatar_url, message)
