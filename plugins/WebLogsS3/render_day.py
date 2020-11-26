import datetime
import glob
import html
import os
import re

FIRST_LOGDATE = {}


def _find_first_logdate(channel):
    # This is slow, and as such, we cache this value. That is completely safe,
    # as logs are only written towards the future. So any past detection works
    # fine.

    filter = f"logs/ChannelLogger/oftc/#{channel}/*"
    year = int(sorted(glob.glob(filter))[0].split("/")[-1])

    filter = f"logs/ChannelLogger/oftc/#{channel}/{year:04d}/*"
    month = int(sorted(glob.glob(filter))[0].split("/")[-1])

    filter = f"logs/ChannelLogger/oftc/#{channel}/{year:04d}/{month:02d}/*"
    day_node = sorted(glob.glob(filter))[0].split("/")[-1]
    day = int(day_node[len(f"#{channel}.{year:04d}{month:02d}") : -len(".log")])

    FIRST_LOGDATE[channel] = datetime.date(year=int(year), month=int(month), day=int(day))


def render_day(base_url, channel, date, has_prev_day=None):
    now = datetime.date.today()

    if channel not in FIRST_LOGDATE:
        _find_first_logdate(channel)

    if date < now:
        next_date = date + datetime.timedelta(days=1)
        link = f"{base_url}/{channel}/{next_date.year:04d}/{next_date.month:02d}/{next_date.day:02d}.html"
        next_day = f'<a class="next" href="{link}">continue to next day ⏵</a>'
    elif date > now:
        next_day = ""
    else:
        next_day = '<span class="next">(this day is still ongoing; reload to check for any updates)</span>'

    if FIRST_LOGDATE[channel] < date:
        prev_date = date - datetime.timedelta(days=1)
        link = f"{base_url}/{channel}/{prev_date.year:04d}/{prev_date.month:02d}/{prev_date.day:02d}.html"
        prev_day = f'<a class="prev" href="{link}">⏴ go to previous day</a>'
    elif FIRST_LOGDATE[channel] == date:
        prev_day = '<span class="prev">(this day is the first day of recording for this channel)</span>'
    else:
        next_day = ""
        prev_day = ""

    if date > now:
        prev_day = ""

    result = f"""
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <link rel="icon" href="/favicon.ico" type="image/icon" />
        <title>IRC Logs | #{channel} | {date.year:04d}-{date.month:02d}-{date.day:02d}</title>
        <link rel="stylesheet" href="/weblogs/css/index.css" type="text/css" />
    </head>
    <body>
        <div class="info">
            IRC logs for #{channel} on OFTC at {date.year:04d}-{date.month:02d}-{date.day:02d}
        </div>
        <div class="breadcrumbs">
            <a href="{base_url}/{channel}/">#{channel}</a> /
            <a href="{base_url}/{channel}/{date.year:04d}/">{date.year:04d}</a> /
            <a href="{base_url}/{channel}/{date.year:04d}/{date.month:02d}/">{date.month:02d}</a>
        </div>
        <pre>
            {prev_day}
"""

    filename = f"#{channel}.{date.year:04d}{date.month:02d}{date.day:02d}"
    filename = f"logs/ChannelLogger/oftc/#{channel}/{date.year:04d}/{date.month:02d}/{filename}.log"
    if not os.path.exists(filename):
        if FIRST_LOGDATE[channel] > date:
            result += '<span class="prev">(this day is from before recording)</span>'
        elif date < now:
            result += '<span class="prev">(nobody has said anything yet today)</span>'
        elif date > now:
            result += '<span class="prev">(this day is in the future)</span>'
        else:
            result += '<span class="prev">(nothing was recorded on this day)</span>'
    else:
        with open(filename, encoding="utf-8", errors="ignore") as fp:
            for lineno, line in enumerate(fp.readlines()):
                dt, _, text = line.split(" ", 2)
                date, time = dt.split("T")

                # Strip out IP-addresses from join/part/quit/..
                if text.startswith("***"):
                    text = re.sub(r"\*\*\* ([^ ]*) <([^>]*)>", r"*** \1", text)

                text = html.escape(text)
                anchor = f'{time.replace(":", "")}-{lineno}'

                classname = "text"
                if text.startswith("***"):
                    # Remove the *** and username
                    _, message = text[4:].split(" ", 1)

                    if message.startswith("is now known as"):
                        classname = "nick"
                    elif message.startswith("invited"):
                        classname = "invite"
                    elif message.startswith("has joined"):
                        classname = "join"
                    elif message.startswith("was kicked by"):
                        classname = "kick"
                    elif message.startswith("has left"):
                        classname = "part"
                    elif message.startswith("sets mode"):
                        classname = "mode"
                    elif message.startswith("changes topic to"):
                        classname = "topic"
                    elif message.startswith("has quit"):
                        classname = "quit"
                    else:
                        classname = "unknown"

                result += f'<div><a class="anchor" name="{anchor}" href="#{anchor}">{time}</a>  '
                result += f'<span class="{classname}">{text}</span></div>\n'

    result += f"{next_day}</pre>\n</body>\n"
    return result
