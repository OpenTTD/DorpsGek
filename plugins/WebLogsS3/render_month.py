import datetime
import glob


def render_month(base_url, channel, date):
    now = datetime.date.today()

    result = f"""
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <link rel="icon" href="/favicon.ico" type="image/icon" />
        <title>IRC Logs | #{channel} | {date.year:04d}-{date.month:02d}</title>
        <link rel="stylesheet" href="/weblogs/css/index.css" type="text/css" />
    </head>
    <body>
        <div class="info">
            IRC logs for #{channel} on OFTC on {date.year:04d}-{date.month:02d}
        </div>
        <div class="breadcrumbs">
            <a href="{base_url}/{channel}/">#{channel}</a> /
            <a href="{base_url}/{channel}/{date.year:04d}/">{date.year:04d}</a>
        </div>
"""

    filter = f"logs/ChannelLogger/oftc/#{channel}/{date.year:04d}/{date.month:02d}/*.log"
    day_nodes = sorted(glob.glob(filter))

    if date > now:
        result += '<pre><span class="prev">(this month is in the future)</span></pre>'
    elif not day_nodes:
        result += '<pre><span class="prev">(nothing was recorded on this month)</span></pre>'
    else:
        result += "<ul>"
        for node in day_nodes:
            day = int(node.split("/")[-1][len(f"#{channel}.{date.year:04d}{date.month:02d}") : -len(".log")])
            entry = datetime.date(year=date.year, month=date.month, day=day)

            link = f"{base_url}/{channel}/{date.year:04d}/{date.month:02d}/{day:02d}.html"
            result += "<li>"
            result += f'<a href="{link}">{date.year:04d}-{date.month:02d}-{day:02d} - {entry.strftime("%A")}</a>'
            result += "</li>"
        result += "</ul>"

    result += "</body>\n"
    return result
