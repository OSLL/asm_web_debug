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


async def create_container(name: str, config: dict) -> str:
    container_id = None

    try:
        async with get_docker_session().post(f"/containers/create?name={name}", json=config) as resp:
            data = await resp.json()
            if "Id" in data:
                container_id = data["Id"]
            else:
                raise DockerError(data["message"])
    except asyncio.CancelledError:
        if container_id:
            await asyncio.shield(stop_and_delete_container(container_id))
        raise

    return container_id


async def start_container(container_id: str) -> None:
    async with get_docker_session().post(f"/containers/{container_id}/start") as resp:
        if resp.status != 204:
            raise DockerError("Failed to start container")


async def stop_and_delete_container(container_id: str) -> None:
    async with get_docker_session().delete(f"/containers/{container_id}?force=true"):
        pass


async def run_command_in_container(container_id: str, command: List[str]) -> bytes:
    config = {
        "AttachStdout": True,
        "AttachStderr": False,
        "AttachStdin": False,
        "Cmd": command
    }

    async with get_docker_session().post(f"/containers/{container_id}/exec", json=config) as resp:
        data = await resp.json()
        if "Id" in data:
            exec_id = data["Id"]
        else:
            raise DockerError(data["message"])

    async with get_docker_session().post(f"/exec/{exec_id}/start", json={}) as resp:
        body = await resp.read()

    # parse docker stream format, https://docs.docker.com/engine/api/v1.41/#operation/ContainerAttach

    result = b""
    while body:
        size, = struct.unpack(">xxxxI", body[:8])
        body = body[8:]
        result += body[:size]
        body = body[size:]

    return result
