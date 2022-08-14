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
                    "content": message,
                    "username": f"{user} (via GitHub)",
                    "avatar_url": avatar_url,
                    "allowed_mentions": {},
                    "flags": 1 << 2,  # SUPPRESS_EMBEDS
                },
            )
            if resp.status != 200:
                log.error(f"Failed to send message to Discord: {resp.status}")


@protocols.register("discord", "pull-request")
async def pull_request(hook_urls, repository_name, url, user, avatar_url, action, pull_id, title, author):
    message = f"**{repository_name}** - "

    if action == "opened":
        message += f":postbox: opened pull request: {url}\n> {title}"
    elif action == "closed":
        message += f":no_entry: closed pull request: {url}\n> {title}"
    elif action == "merged":
        message += f":rocket: merged pull request: {url}\n> {title}"
    elif action == "synchronize":
        message += f":mega: updated pull request: {url}\n> {title}"
    elif action == "reopened":
        message += f":mailbox_with_mail: reopened pull request: {url}\n> {title}"
    elif action == "comment":
        message += f":speech_balloon: commented on pull request: {url}\n> {title}"
    elif action == "dismissed":
        message += f":eyes: dismissed a review for pull request: {url}\n> {title}"
    elif action == "approved":
        message += f":thumbsup: approved pull request: {url}\n> {title}"
    elif action == "changes_requested":
        message += f":negative_squared_cross_mark: requested changes for pull request: {url}\n> {title}"
    elif action == "commented":
        message += f":speech_balloon: commented on pull request: {url}\n> {title}"
    else:
        return

    await _send_messages(hook_urls, user, avatar_url, message)


@protocols.register("discord", "push")
async def push(hook_urls, repository_name, url, user, avatar_url, branch, commits):
    if len(commits) == 1:
        commit_text = "a commit"
    else:
        commit_text = f"{len(commits)} commits"

    message = f"**{repository_name}** - :muscle: pushed {commit_text} to `{branch}`: {url}\n> "
    message += "\n> ".join([f"{commit['message']} (by {commit['author']})" for commit in commits])

    await _send_messages(hook_urls, user, avatar_url, message)


@protocols.register("discord", "issue")
async def issue(hook_urls, repository_name, url, user, avatar_url, action, issue_id, title, reason):
    message = f"**{repository_name}** - "

    if action == "opened":
        message += f":beetle: opened issue: {url}\n> {title}"
    elif action == "reopened":
        message += f":scream_cat: reopened issue: {url}\n> {title}"
    elif action == "closed":
        if reason == "completed":
            message += f":sunglasses: closed issue: {url}\n> {title}"
        else:
            message += f":triumph: closed issue: {url}\n> {title}"
    elif action == "comment":
        message += f":speech_balloon: commented on issue: {url}\n> {title}"
    else:
        return

    await _send_messages(hook_urls, user, avatar_url, message)


@protocols.register("discord", "discussion")
async def discussion(hook_urls, repository_name, url, user, avatar_url, action, discussion_id, title):
    message = f"**{repository_name}** - "

    if action == "created":
        message += f":speaking_head: started discussion: {url}\n> {title}"
    elif action == "comment":
        message += f":speech_balloon: commented on discussion: {url}\n> {title}"
    else:
        return

    await _send_messages(hook_urls, user, avatar_url, message)


@protocols.register("discord", "commit-comment")
async def commit_comment(hook_urls, repository_name, url, user, avatar_url, message):
    message = f"**{repository_name}** - "
    message += f":open_mouth: left a comment on commit: {url}\n> {message}"

    await _send_messages(hook_urls, user, avatar_url, message)


@protocols.register("discord", "branch-created")
async def ref_branch_created(hook_urls, repository_name, url, user, avatar_url, name):
    message = f"**{repository_name}** - "
    message += f":cow: created a new branch `{name}`: {url}"

    await _send_messages(hook_urls, user, avatar_url, message)


@protocols.register("discord", "tag-created")
async def ref_tag_created(hook_urls, repository_name, url, user, avatar_url, name):
    message = f"**{repository_name}** - "
    message += f":tada: created a new tag `{name}`: {url}"

    await _send_messages(hook_urls, user, avatar_url, message)
