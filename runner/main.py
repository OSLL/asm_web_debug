import asyncio
import logging
import weakref

from aiohttp import web, WSCloseCode
import prometheus_client

from runner.routes import setup_routes
from runner.settings import config
import runner.checkers # register all checkers


async def on_startup(app):
    from runner.monitoring import periodically_update_resource_usage_gauges
    app["monitoring_task"] = asyncio.create_task(periodically_update_resource_usage_gauges())


async def on_shutdown(app):
    from runner.docker import get_docker_session
    from runner.wsinteractor import get_flask_session
    await get_docker_session().close()
    await get_flask_session().close()

    for ws in set(app['websockets']):
        await ws.close(code=WSCloseCode.GOING_AWAY,
                       message='Server shutdown')

    app["monitoring_task"].cancel()


def init_app() -> web.Application:
    app = web.Application()
    app["websockets"] = weakref.WeakSet()
    app.on_startup.append(on_startup)
    app.on_shutdown.append(on_shutdown)

    setup_routes(app)

    return app


def main() -> None:
    logging.basicConfig(level=logging.os.environ.get('LOGLEVEL', 'INFO').upper())

    prometheus_client.start_http_server(config.prometheus_port)

    app = init_app()
    web.run_app(app, host=config.host, port=config.port)
