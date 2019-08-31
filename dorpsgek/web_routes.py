import logging

from aiohttp import web
from dorpsgek.helpers import github

log = logging.getLogger(__name__)
routes = web.RouteTableDef()


@routes.post('/')
async def github_handler(request):
    headers = request.headers
    data = await request.read()

    try:
        await github.dispatch(headers, data)
        return web.HTTPOk()
    except Exception:
        log.exception("Failed to handle GitHub event")
        return web.HTTPInternalServerError()


@routes.route('*', '/{tail:.*}')
async def fallback(request):
    log.warning('Unexpected URL: %s', request.url)
    return web.HTTPNotFound()
