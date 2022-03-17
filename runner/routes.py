from aiohttp import web

from runner import views


def setup_routes(app: web.Application):
    app.router.add_get("/runner_api/websocket", views.ide_websocket)
    app.router.add_post("/runner_api/check", views.api_check)
