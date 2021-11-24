import contextlib

from quart import websocket, Blueprint, current_app

from app.core.process_manager import ProcessManager

bp = Blueprint("debug", __name__)


@bp.websocket("/ws")
async def debug_ws():
    process = None
    with contextlib.AsyncExitStack() as cleanup:
        async def _do_cleanup():
            if process is not None:
                await process.aclose()
        cleanup.push_async_callback(_do_cleanup)

        while True:
            data = await websocket.receive_json()
            if data["cmd"] == "start_debug":
                assert data["arch"] in current_app.config["ARCHS"]
                assert data["src"] is str
                process = ProcessManager.start_debugging(data["src"], data["arch"])
