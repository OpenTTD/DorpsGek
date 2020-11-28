from supybot import callbacks, httpserver
from supybot.commands import wrap

# Minimize the amount of valid endpoints
if httpserver.http_servers and ".well-known" in httpserver.http_servers[0].callbacks:
    del httpserver.http_servers[0].callbacks[".well-known"]


# Overwrite the original do_X. It does all kinds of weird stuff, like an
# overview page which plugins are loaded, and CSS, and more of that ..
# minimize what is open to the Internet, only respond to URLs we expect.
def patched_do_X(self, callbackMethod, *args, **kwargs):
    if self.path == "/healthz":
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"200: OK")
        return

    if self.path == "/robots.txt":
        self.send_response(200)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"User-agent: *\nDisallow: /")
        return

    if self.path.count("/") <= 1:
        self.send_response(404)
        self.send_header("Content-Type", "text/plain")
        self.end_headers()
        self.wfile.write(b"404: page not found")
        return

    httpserver.original_do_X(self, callbackMethod, *args, **kwargs)


# Only log requests that hit an error code
def patched_log_message(self, format, *args):
    if not (200 <= int(args[1]) < 400):
        httpserver.original_log_message(self, format, *args)


# Ensure we only capture the original function once; this plugin can be
# reloaded many times.
if not hasattr(httpserver, "original_do_X"):
    httpserver.original_do_X = httpserver.SupyHTTPRequestHandler.do_X
    httpserver.original_log_message = httpserver.SupyHTTPRequestHandler.log_message
httpserver.SupyHTTPRequestHandler.do_X = patched_do_X
httpserver.SupyHTTPRequestHandler.log_message = patched_log_message


class OpenTTD(callbacks.Plugin):
    """Some commands specific for OpenTTD channels."""

    def ports(self, irc, msg, args):
        """takes no arguments"""
        irc.reply(
            "OpenTTD uses TCP and UDP port 3979 for server <-> client communication, "
            "UDP port 3978 for masterserver (advertise) communication (outbound), "
            "and TCP port 3978 for content service, a.k.a. BaNaNaS (outbound)"
        )

    ports = wrap(ports)


Class = OpenTTD
