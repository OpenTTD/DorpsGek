import datetime
import glob


def render_year(base_url, channel, date):
    now = datetime.date.today()

    result = f"""
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <link rel="icon" href="/favicon.ico" type="image/icon" />
        <title>IRC Logs | #{channel} | {date.year:04d}</title>
        <link rel="stylesheet" href="/weblogs/css/index.css" type="text/css" />
    </head>
    <body>
        <div class="info">
            IRC logs for #{channel} on OFTC in {date.year:04d}
        </div>
        <div class="breadcrumbs">
            <a href="{base_url}/{channel}/">#{channel}</a>
        </div>
"""

    filter = f"logs/ChannelLogger/oftc/#{channel}/{date.year:04d}/*"
    month_nodes = sorted(glob.glob(filter))

    if date > now:
        result += '<pre><span class="prev">(this year is in the future)</span></pre>'
    elif not month_nodes:
        result += '<pre><span class="prev">(nothing was recorded on this year)</span></pre>'
    else:
        result += "<ul>"
        for node in month_nodes:
            month = int(node.split("/")[-1])
            entry = datetime.date(year=date.year, month=month, day=1)

            link = f"{base_url}/{channel}/{date.year:04d}/{month:02d}/"
            result += "<li>"
            result += f'<a href="{link}">{date.year:04d}-{month:02d} - {entry.strftime("%B")}</a>'
            result += "</li>"
        result += "</ul>"

    result += "</body>\n</html>\n"
    return result
