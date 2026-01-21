import calendar
import datetime

from supybot import callbacks, httpserver
from supybot.commands import wrap

from . import settings
from .render_channel import render_channel
from .render_day import render_day
from .render_list import render_list
from .render_month import render_month
from .render_year import render_year

# Please change the "last modified" date below when making any changes to the CSS.
INDEX_CSS = """
body {
    margin: auto;
    max-width: 1020px;
    padding: 10px;
}
a {
    color: #DD6000;
}
a:hover, a:focus {
    color: #BB4000;
}
pre, ul {
    border: 1px solid #aaa;
    clear: both;
    list-style: none;
    padding: 10px 10px;
    white-space: normal;
}
pre a.anchor {
    margin-left: -90px;
}
pre .next {
    display: block;
    padding: 20px 0 0 20px;
}
pre .prev {
    display: block;
    padding: 0 0 20px 20px;
}
pre div {
    margin-left: 90px;
}
pre div span {
    margin-left: 10px;
}

.info {
    float: left;
    margin-bottom: 10px;
}
.breadcrumbs {
    float: right;
    text-align: right;
}

.text {
    color: black;
}
.nick {
    color: blue;
}
.invite {
    color: blue;
}
.join {
    color: green;
}
.kick {
    color: maroon;
}
.part {
    color: maroon;
}
.mode {
    color: blue;
}
.topic {
    color: blue;
}
.quit {
    color: maroon;
}
"""


class WebLogsS3Callback(httpserver.SupyHTTPServerCallback):
    name = "WebLogsS3"
    defaultResponse = "404: page not found"

    def __init__(self):
        self.start_time = datetime.datetime.now()

    def render_html(self, path):
        base_url = settings.WEB_LOGS_URL or "/weblogs"
        spath = path.split("/")
        now = datetime.date.today()

        html = ""
        headers = {}

        if len(spath) == 2 and spath[-1] == "":
            html = render_list(base_url)

            # This page was last modified when we started the bot.
            headers["Last-Modified"] = self.start_time.strftime("%a, %d %b %Y %H:%M:%S GMT")
            headers["Cache-Control"] = "public, max-age=86400"

        elif f"#{spath[1]}" in settings.PUBLIC_CHANNELS:
            if len(spath) == 3 and spath[-1] == "":
                _, channel, _ = spath

                html = render_channel(base_url, channel)

                # This page has a reference to "today".
                headers["Last-Modified"] = now.strftime("%a, %d %b %Y %H:%M:%S GMT")
                headers["Cache-Control"] = "public, max-age=86400"

            if len(spath) == 4 and spath[-1] == "":
                _, channel, year, _ = spath

                if year.isdecimal():
                    year = int(year)
                    request = datetime.date(year=year, month=1, day=1)
                    html = render_year(base_url, channel, request)

                    if request > now:
                        headers["Cache-Control"] = "no-cache"
                    else:
                        if request.year == now.year:
                            # If this is the current year, last 00:00 was when
                            # this page was last modified.
                            last_modified = now
                        else:
                            # If this is any other year, the first day of the
                            # next year was the last modified.
                            days_in_year = 366 if calendar.isleap(request.year) else 365
                            last_modified = request + datetime.timedelta(days=days_in_year)

                        headers["Last-Modified"] = last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
                        headers["Cache-Control"] = "public, max-age=86400"

            elif len(spath) == 5 and spath[-1] == "":
                _, channel, year, month, _ = spath

                if year.isdecimal() and month.isdecimal():
                    year = int(year)
                    month = int(month)
                    request = datetime.date(year=year, month=month, day=1)
                    html = render_month(base_url, channel, request)

                    if request > now:
                        headers["Cache-Control"] = "no-cache"
                    else:
                        if request.year == now.year and request.month == now.month:
                            # If this is the current month, last 00:00 was when
                            # this page was last modified.
                            last_modified = now
                        else:
                            # If this is any other month, the first day of the
                            # next month was the last modified.
                            days_in_month = calendar.monthrange(request.year, request.month)[1]
                            last_modified = request + datetime.timedelta(days=days_in_month)

                        headers["Last-Modified"] = last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
                        headers["Cache-Control"] = "public, max-age=86400"

            elif len(spath) == 5:
                _, channel, year, month, day = spath

                if day.endswith(".html"):
                    day = day[: -len(".html")]

                    if year.isdecimal() and month.isdecimal() and day.isdecimal():
                        year = int(year)
                        month = int(month)
                        day = int(day)
                        request = datetime.date(year=year, month=month, day=day)

                        html = render_day(base_url, channel, request)

                        # Only today should not be cached; all other pages are fine
                        # to cache for a longer period of time, as they will not be
                        # changing any time soon.
                        if request >= now:
                            headers["Cache-Control"] = "no-cache"
                        else:
                            last_modified = request + datetime.timedelta(days=1)
                            headers["Last-Modified"] = last_modified.strftime("%a, %d %b %Y %H:%M:%S GMT")
                            headers["Cache-Control"] = "public, max-age=86400"

        return html, headers

    def doGet(self, handler, path):
        if path == "/css/index.css":
            self.send_response(200)
            self.send_header("Content-Type", "text/css")
            # Please change this date whenever the CSS is changed.
            self.send_header("Last-Modified", "Mon, 08 Aug 2022 00:00:00 GMT")
            self.send_header("Cache-Control", "public, max-age=86400")
            self.end_headers()
            self.wfile.write(INDEX_CSS.encode())
            return

        try:
            html, headers = self.render_html(path)
        except ValueError:
            # Someone entered an invalid date in the path. We just let it fallthrough to the 404 page.
            html = ""
            headers = {}

        if not html:
            self.send_response(404)
            self.send_header("Content-type", "text/plain")
            self.end_headers()
            self.wfile.write(b"404: page not found")
            return

        self.send_response(200)
        self.send_header("Content-Type", "text/html")
        self.send_header("Content-Security-Policy", "default-src 'self'")
        for key, value in headers.items():
            self.send_header(key, value)
        self.end_headers()
        self.wfile.write(html.encode())


class WebLogsS3(callbacks.Plugin):
    """Generate weblogs and publish them to S3 daily."""

    def __init__(self, irc):
        self.__parent = super(WebLogsS3, self)
        callbacks.Plugin.__init__(self, irc)

        httpserver.hook("weblogs", WebLogsS3Callback())

    def die(self):
        self.__parent.die()
        httpserver.unhook("weblogs")

    def logs(self, irc, msg, args, channel):
        """[<channel>]

        Returns the URL to find the public IRC logs for that channel.
        """

        if not settings.WEB_LOGS_URL:
            return

        if channel not in settings.PUBLIC_CHANNELS:
            irc.reply(f"I do not have a public log for {channel}")
        else:
            irc.reply(f"{settings.WEB_LOGS_URL}/{channel[1:]}/")

    logs = wrap(logs, ["channel"])


Class = WebLogsS3
