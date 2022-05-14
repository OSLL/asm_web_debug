import asyncio
import logging
import weakref

from aiohttp import web, WSCloseCode
import prometheus_client

from runner.routes import setup_routes
from runner.settings import config
import runner.checkers # register all checkers


async def on_shutdown(app):
    from runner.docker import get_docker_session
    from runner.wsinteractor import get_flask_session
    from runner.runner import active_debug_sessions
    await get_docker_session().close()
    await get_flask_session().close()

    for ws in set(app['websockets']):
        await ws.close(code=WSCloseCode.GOING_AWAY,
                       message='Server shutdown')

    for session in list(active_debug_sessions):
        try:
            await session.close()
        except:
            pass


def init_app() -> web.Application:
    app = web.Application()
    app["websockets"] = weakref.WeakSet()
    app.on_shutdown.append(on_shutdown)

    setup_routes(app)

    return app


def main() -> None:
    logging.basicConfig(
        level=logging.os.environ.get('LOGLEVEL', 'INFO').upper(),
        format="%(asctime)s [%(levelname)s] %(message)s"
    )

    prometheus_client.start_http_server(config.prometheus_port)

    app = init_app()
    web.run_app(app, host=config.host, port=config.port)
