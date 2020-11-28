from . import settings


def render_list(base_url):
    result = """
<!doctype html>
<html lang="en">
    <head>
        <meta charset="utf-8">
        <link rel="icon" href="/favicon.ico" type="image/icon" />
        <title>IRC Logs</title>
        <link rel="stylesheet" href="/weblogs/css/index.css" type="text/css" />
    </head>
    <body>
        <div class="info">
            IRC logs on OFTC
        </div>
"""

    if not settings.PUBLIC_CHANNELS:
        result += '<pre><span class="prev">(nothing was recorded)</span></pre>'
    else:
        result += "<ul>"
        for channel in settings.PUBLIC_CHANNELS:
            result += "<li>"
            result += f'<a href="{base_url}/{channel[1:]}/">{channel}</a>'
            result += "<li>"
        result += "</ul>"

    result += "</body>\n"
    return result
