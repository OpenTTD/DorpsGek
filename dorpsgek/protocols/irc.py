import irc3

from dorpsgek.helpers import protocols
from dorpsgek.helpers.url import shorten

irc_connection = None


def startup():
    global irc_connection

    cfg = irc3.utils.parse_config("bot", "dorpsgek.ini")
    irc_connection = irc3.IrcBot.from_config(cfg)
    irc_connection.run(forever=False)


@protocols.register("irc", "pull-request")
async def pull_request(channels, repository_name, url, user, action, pull_id, title):
    channels = [f"#{c}" for c in channels]

    autojoins = irc_connection.get_plugin("irc3.plugins.autojoins.AutoJoins")

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

    for channel in channels:
        # Try to join the channel before we send a message
        if channel not in autojoins.joined:
            autojoins.join(channel)

        shortened_url = await shorten(url)
        irc_connection.privmsg(channel, f"[{repository_name}] {message} {shortened_url}")


@protocols.register("irc", "push")
async def push(channels, repository_name, url, user, branch, commits):
    channels = [f"#{c}" for c in channels]

    autojoins = irc_connection.get_plugin("irc3.plugins.autojoins.AutoJoins")

    commit_count = len(commits)

    for channel in channels:
        # Try to join the channel before we send a message
        if channel not in autojoins.joined:
            autojoins.join(channel)

        shortened_url = await shorten(url)
        irc_connection.privmsg(
            channel,
            f"[{repository_name}] {user} pushed {commit_count} commits to {branch} {shortened_url}"
        )
        for commit in commits:
            irc_connection.privmsg(channel, f"  - {commit['message']} (by {commit['author']})")


@protocols.register("irc", "issue")
async def issue(channels, repository_name, url, user, action, issue_id, title):
    channels = [f"#{c}" for c in channels]

    autojoins = irc_connection.get_plugin("irc3.plugins.autojoins.AutoJoins")

    if action == "opened":
        message = f"{user} opened issue #{issue_id}: {title}"
    elif action == "reopened":
        message = f"{user} reopened issue #{issue_id}: {title}"
    elif action == "closed":
        message = f"{user} closed issue #{issue_id}: {title}"
    elif action == "comment":
        message = f"{user} commented on issue #{issue_id}: {title}"

    for channel in channels:
        # Try to join the channel before we send a message
        if channel not in autojoins.joined:
            autojoins.join(channel)

        shortened_url = await shorten(url)
        irc_connection.privmsg(channel, f"[{repository_name}] {message} {shortened_url}")
