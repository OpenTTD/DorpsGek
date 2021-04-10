from supybot import ircmsgs, world

from ..helpers import protocols
from ..helpers.url import shorten


def _send_messages(channels, messages):
    channels = [f"#{c}" for c in channels]

    for irc in world.ircs:
        for channel in channels:
            for message in messages:
                irc.queueMsg(ircmsgs.privmsg(channel, message))


@protocols.register("irc", "pull-request")
async def pull_request(channels, repository_name, url, user, action, pull_id, title):
    if action == "opened":
        message = f"{user} opened pull request #{pull_id}: {title}"
    elif action == "closed":
        message = f"{user} closed pull request #{pull_id}: {title}"
    elif action == "merged":
        message = f"{user} merged pull request #{pull_id}: {title}"
    elif action == "synchronize":
        message = f"{user} updated pull request #{pull_id}: {title}"
    elif action == "reopened":
        message = f"{user} reopened pull request #{pull_id}: {title}"
    elif action == "comment":
        message = f"{user} commented on pull request #{pull_id}: {title}"
    elif action == "dismissed":
        message = f"{user} dismissed a review for pull request #{pull_id}: {title}"
    elif action == "approved":
        message = f"{user} approved pull request #{pull_id}: {title}"
    elif action == "changes_requested":
        message = f"{user} requested changes for pull request #{pull_id}: {title}"
    elif action == "commented":
        message = f"{user} commented on pull request #{pull_id}: {title}"
    else:
        return

    shortened_url = await shorten(url)
    _send_messages(channels, [f"[{repository_name}] {message} {shortened_url}"])


@protocols.register("irc", "push")
async def push(channels, repository_name, url, user, branch, commits):
    commit_count = len(commits)

    shortened_url = await shorten(url)
    _send_messages(
        channels,
        [f"[{repository_name}] {user} pushed {commit_count} commits to {branch} {shortened_url}"]
        + [f"  - {commit['message']} (by {commit['author']})" for commit in commits],
    )


@protocols.register("irc", "issue")
async def issue(channels, repository_name, url, user, action, issue_id, title):
    if action == "opened":
        message = f"{user} opened issue #{issue_id}: {title}"
    elif action == "reopened":
        message = f"{user} reopened issue #{issue_id}: {title}"
    elif action == "closed":
        message = f"{user} closed issue #{issue_id}: {title}"
    elif action == "comment":
        message = f"{user} commented on issue #{issue_id}: {title}"
    else:
        return

    shortened_url = await shorten(url)
    _send_messages(channels, [f"[{repository_name}] {message} {shortened_url}"])


@protocols.register("irc", "discussion")
async def discussion(channels, repository_name, url, user, action, discussion_id, title):
    if action == "created":
        message = f"{user} started discussion #{discussion_id}: {title}"
    elif action == "comment":
        message = f"{user} commented on discussion #{discussion_id}: {title}"
    else:
        return

    shortened_url = await shorten(url)
    _send_messages(channels, [f"[{repository_name}] {message} {shortened_url}"])


@protocols.register("irc", "commit-comment")
async def commit_comment(channels, repository_name, url, user, message):
    message = f"{user} left a comment on commit: {message}"

    shortened_url = await shorten(url)
    _send_messages(channels, [f"[{repository_name}] {message} {shortened_url}"])


@protocols.register("irc", "branch-created")
async def ref_branch_created(channels, repository_name, url, user, name):
    shortened_url = await shorten(url)
    _send_messages(
        channels,
        [f"[{repository_name}] {user} created new branch: {name} {shortened_url}"],
    )


@protocols.register("irc", "tag-created")
async def ref_tag_created(channels, repository_name, url, user, name):
    shortened_url = await shorten(url)
    _send_messages(
        channels,
        [f"[{repository_name}] {user} created new tag: {name} {shortened_url}"],
    )
