from aiohttp import web
from runner.checkerlib import Checker

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


async def api_check(request: web.Request):
    params = await request.json()

    try:
        await Checker.run_checker(**params)
    except Exception as e:
        return web.json_response({
            "ok": False,
            "message": str(e),
            "error_type": e.__class__.__name__
        })

    return web.json_response({
        "ok": True
    })
