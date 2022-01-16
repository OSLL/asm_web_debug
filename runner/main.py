import logging
import weakref

from aiohttp import web, WSCloseCode

from runner.routes import setup_routes
from runner.settings import config


async def on_shutdown(app):
    for ws in set(app['websockets']):
        await ws.close(code=WSCloseCode.GOING_AWAY,
                       message='Server shutdown')


def init_app() -> web.Application:
    app = web.Application()
    app["websockets"] = weakref.WeakSet()
    app.on_shutdown.append(on_shutdown)

    setup_routes(app)

    return app


def main():
    logging.basicConfig(level=logging.DEBUG)

    app = init_app()
    web.run_app(app, host=config.host, port=config.port)
