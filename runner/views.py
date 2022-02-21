from aiohttp import web

from runner.wsinteractor import WSInteractor, run_interactor


async def ide_websocket(request: web.Request):
    ws = web.WebSocketResponse()
    await ws.prepare(request)

    request.app["websockets"].add(ws)

    try:
        await run_interactor(ws)
    finally:
        request.app["websockets"].discard(ws)

    return ws
