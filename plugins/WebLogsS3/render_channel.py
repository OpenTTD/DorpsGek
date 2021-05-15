import datetime
import glob


def render_channel(base_url, channel):
    now = datetime.date.today()

    result = f"""
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <link rel="icon" href="/favicon.ico" type="image/icon" />
        <title>IRC Logs | #{channel}</title>
        <link rel="stylesheet" href="/weblogs/css/index.css" type="text/css" />
    </head>
    <body>
        <div class="info">
            IRC logs for #{channel} on OFTC
        </div>
"""

    filter = f"logs/ChannelLogger/oftc/#{channel}/*"
    year_nodes = sorted(glob.glob(filter))

    if not year_nodes:
        result += '<pre><span class="prev">(nothing was recorded for this channel)</span></pre>'
    else:
        result += "<ul>"
        result += f'<li><a href="{base_url}/{channel}/{now.year}/{now.month}/{now.day}.html">Jump to today</a></li>'
        result += "</ul>"

        result += "<ul>"
        for node in year_nodes:
            year = int(node.split("/")[-1])
            result += "<li>"
            result += f'<a href="{base_url}/{channel}/{year:04d}/">{year:04d}</a>'
            result += "<li>"
        result += "</ul>"

    result += "</body>\n</html>\n"
    return result
