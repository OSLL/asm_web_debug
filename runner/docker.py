import asyncio
import struct
from typing import List, Optional

import aiohttp

from runner.settings import config


_docker_session: Optional[aiohttp.ClientSession] = None

def get_docker_session() -> aiohttp.ClientSession:
    global _docker_session
    if not _docker_session:
        _docker_session = aiohttp.ClientSession(
            base_url="http://docker",
            connector=aiohttp.UnixConnector(config.docker_socket)
        )
    return _docker_session


class DockerError(Exception): pass


async def create_and_start_container(config: dict) -> str:
    container_id = None

    try:
        async with get_docker_session().post("/containers/create", json=config) as resp:
            data = await resp.json()
            if "Id" in data:
                container_id = data["Id"]
            else:
                raise DockerError(data["message"])

        async with get_docker_session().post(f"/containers/{container_id}/start") as resp:
            if resp.status != 204:
                raise DockerError("Failed to start container")
    except asyncio.CancelledError:
        if container_id:
            await asyncio.shield(stop_and_delete_container(container_id))
        raise

    return container_id


async def stop_and_delete_container(container_id: str) -> None:
    async with get_docker_session().delete(f"/containers/{container_id}?force=true"):
        pass
