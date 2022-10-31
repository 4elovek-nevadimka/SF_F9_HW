import os

from aiohttp import web

WS_FILE = os.path.join(os.path.dirname(__file__), "../client/client.html")
# curl --data "Greta Thunberg isn’t going to COP27. Here’s why" http://0.0.0.0:8080/news

routes = web.RouteTableDef()


@routes.post('/news')
async def post_news(request):
    if request.body_exists:
        for ws in request.app["sockets"]:
            await ws.send_str(await request.text())
    return web.Response(status=200)


@routes.get('/ws')
async def websocket_handler(request):

    ws_response = web.WebSocketResponse(autoping=True, heartbeat=60)
    available = ws_response.can_prepare(request)
    if not available:
        with open(WS_FILE, "rb") as fp:
            return web.Response(body=fp.read(), content_type="text/html")

    await ws_response.prepare(request)

    try:
        request.app["sockets"].append(ws_response)

        async for msg in ws_response:
            if msg.type == web.WSMsgType.TEXT:
                for ws in request.app["sockets"]:
                    if ws is not ws_response:
                        await ws.send_str(msg.data)
            else:
                return ws_response
        return ws_response

    finally:
        request.app["sockets"].remove(ws_response)


async def on_shutdown(app: web.Application):
    for ws in app["sockets"]:
        await ws.close()


def run_app():
    app = web.Application()
    app["sockets"] = []
    app.add_routes(routes)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app)


run_app()
