import base64
import click
import os
import subprocess
import sys

from openttd_helpers import click_helper
from openttd_helpers.sentry_helper import click_sentry


@click_helper.command()
@click_sentry
@click.option("--github-app-id", help="GitHub App ID")
@click.option("--github-app-private-key", help="GitHub App Private Key")
@click.option(
    "--github-app-private-key-file",
    help="GitHub App Private Key",
    type=click.Path(exists=True, dir_okay=False),
)
@click.option("--github-app-secret", help="GitHub App Secret")
@click.option("--irc-username", help="Nick to use on IRC", default="DorpsGek_dev")
@click.option("--nickserv-username", help="Username as known by NickServ")
@click.option("--nickserv-password", help="Password for --nickserv-username")
@click.option("--addressed-by", help="What symbol addresses the bot?", default="!")
@click.option("--web-logs-url", help="URL where the weblogs are stored (https://...)")
@click.option(
    "--channel",
    help="What IRC channel to join (postfix with ',public' to make it browseable on the web)",
    multiple=True,
    default=["dorpsgek-test"],
)
@click.option("--discord-webhook-url", help="URL to the Discord webhook")
@click.option("--discord-unfiltered-webhook-url", help="URL to the Discord webhook that receives all events")
@click.option("--port", help="Port of the server", default=80, show_default=True)
def main(
    github_app_id,
    github_app_private_key,
    github_app_private_key_file,
    github_app_secret,
    irc_username,
    nickserv_username,
    nickserv_password,
    addressed_by,
    web_logs_url,
    channel,
    discord_webhook_url,
    discord_unfiltered_webhook_url,
    port,
):
    if github_app_private_key_file:
        with open(github_app_private_key_file, "rb") as fp:
            github_private_key = fp.read()
    elif github_app_private_key:
        github_private_key = base64.b64decode(github_app_private_key)
    else:
        github_private_key = ""

    if web_logs_url and web_logs_url.endswith("/"):
        web_logs_url = web_logs_url[:-1]

    # Store this information inside the plugin, so it can be loaded.
    with open("plugins/GitHub/settings.py", "w") as fp:
        fp.write(f"GITHUB_APP_SECRET = {github_app_secret!r}\n")
        fp.write(f"GITHUB_APP_ID = {github_app_id!r}\n")
        fp.write(f"GITHUB_APP_PRIVATE_KEY = {github_private_key!r}\n")
        fp.write(f"DISCORD_WEBHOOK_URL = {discord_webhook_url!r}\n")
        fp.write(f"DISCORD_UNFILTERED_WEBHOOK_URL = {discord_unfiltered_webhook_url!r}\n")

    with open("plugins/WebLogsS3/settings.py", "w") as fp:
        public_channels = [f"#{c.split(',')[0]}" for c in set(channel) if c.endswith(",public")]
        fp.write(f"PUBLIC_CHANNELS = {public_channels!r}\n")
        fp.write(f"WEB_LOGS_URL = {web_logs_url!r}\n")

    # What information to replace in the configuration files.
    replace = {
        "HttpPort": str(port),
        "Username": irc_username,
        "NickServ_Username": nickserv_username or "",
        "NickServ_Password": nickserv_password or "",
        "AddressBy": addressed_by,
        "Channels": " ".join([f"#{c.split(',')[0]}" for c in set(channel)]),
    }

    # Create a generated configuration with the right items replaced.
    with open("DorpsGek.conf") as fp_read:
        with open("DorpsGek-generated.conf", "w") as fp_write:
            for line in fp_read.readlines():
                for name, value in replace.items():
                    line = line.replace("{{" + name + "}}", value)

                fp_write.write(line)

    # Ensure the bot runs in UTC.
    env = os.environ.copy()
    env["TZ"] = "UTC"

    # We allow to run as root, as this is most likely running in a Docker.
    result = subprocess.run(["supybot", "DorpsGek-generated.conf", "--allow-root"], env=env)
    sys.exit(result.returncode)


if __name__ == "__main__":
    main(auto_envvar_prefix="DORPSGEK")
