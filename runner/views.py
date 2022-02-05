from aiohttp import web
from runner.checkerlib import BaseChecker, CheckerException

from runner.wsinteractor import run_interactor


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
        await BaseChecker.run_checker_by_name(**params)
    except CheckerException as err:
        return web.json_response({
            "ok": False,
            "message": str(err),
            "error_type": err.__class__.__name__
        })

    return web.json_response({
        "ok": True
    })
