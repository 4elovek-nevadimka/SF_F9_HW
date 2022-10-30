import os

from aiohttp import web

WS_FILE = os.path.join(os.path.dirname(__file__), "../client/client.html")

routes = web.RouteTableDef()


@routes.get('/hello')
async def hello(request):
    for ws in request.app["sockets"]:
        await ws.send_str("Hello world")
    return web.Response(text="Hello, world")


@routes.post('/news')
async def post_news(request):
    if request.body_exists:
        for ws in request.app["sockets"]:
            await ws.send_str(await request.text())
        # print(await request.text())
    return web.Response(status=200)


@routes.get('/ws')
async def websocket_handler(request):

    ws_response = web.WebSocketResponse()

    available = ws_response.can_prepare(request)
    if not available:
        with open(WS_FILE, "rb") as fp:
            return web.Response(body=fp.read(), content_type="text/html")

    await ws_response.prepare(request)

    try:
        # for ws in request.app["sockets"]:
        #     await ws.send_str("Someone joined")
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
        # for ws in request.app["sockets"]:
        #     await ws.send_str("Someone disconnected.")


async def on_shutdown(app: web.Application):
    for ws in app["sockets"]:
        await ws.close()


def run_app():
    app = web.Application()
    app["sockets"] = []
    # app.add_routes([web.get('/', hello)])
    # app.add_routes([web.get('/ws', websocket_handler)])
    app.add_routes(routes)
    app.on_shutdown.append(on_shutdown)
    web.run_app(app)


run_app()
