import asyncio

from supybot import callbacks, httpserver, log

from .helpers import github

# Import files that will hook themself up when imported
from .events import (  # noqa
    commit_comment,
    discussion,
    issue,
    pull_request,
    push,
    tag,
)
from .patches import gidgethub  # noqa
from .protocols import irc as irc_protocols  # noqa


class GitHubCallback(httpserver.SupyHTTPServerCallback):
    name = "GitHub"
    defaultResponse = "404: page not found"

    def doPost(self, handler, path, form):
        if path != "/":
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404: page not found")
            return

        headers = {key.lower(): value for key, value in dict(self.headers).items()}

        try:
            asyncio.run(github.dispatch(headers, form))

            self.send_response(200)
            self.send_header("Content-Type", "text/plain")
            self.end_headers()
            self.wfile.write(b"200: OK")
        except Exception:
            log.exception("Failed to handle GitHub event")
            self.send_response(403)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"403: failed processing event")


class GitHub(callbacks.Plugin):
    """Translates GitHub events to IRC messages."""

    def __init__(self, irc):
        self.__parent = super(GitHub, self)
        callbacks.Plugin.__init__(self, irc)

        httpserver.hook("github", GitHubCallback())

    def die(self):
        self.__parent.die()
        httpserver.unhook("github")


Class = GitHub
