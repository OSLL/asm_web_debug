from aiohttp import web

from runner import views


def setup_routes(app: web.Application):
    app.router.add_get("/ws_ide", views.ide_websocket)
