#!/usr/bin/env python3

import asyncio
from contextlib import asynccontextmanager
import time
from typing import List
import aiohttp
import click


EXAMPLE_SOURCE = r"""
mov $10, %rax

again:
dec %rax
test %rax, %rax
jz end
jmp again

end: nop
"""


class DebugClient:
    ws: aiohttp.ClientWebSocketResponse

    def __init__(self, ws: aiohttp.ClientWebSocketResponse) -> None:
        self.ws = ws

    async def start(self, source_code: str, breakpoints: List[int]) -> bool:
        await self.ws.send_json({
            "type": "run",
            "source": source_code,
            "input": "",
            "breakpoints": breakpoints,
            "sample_test": None
        })
        data = await self.ws.receive_json()
        assert data["type"] == "compilation_result"
        return data["successful"]

    async def wait_until_stopped(self) -> bool:
        while True:
            data = await self.ws.receive_json()
            if data["type"] == "paused":
                return True
            if data["type"] == "finished":
                return False

    async def step(self):
        await self.ws.send_json({"type": "step_over"})


@asynccontextmanager
async def report_time(name: str) -> None:
    now = time.monotonic()
    try:
        yield
    finally:
        print(f"{name} {time.monotonic() - now}")


@click.command()
@click.option("--endpoint", default="http://localhost:8080", help="Endpoint for ASM WEB IDE launched in test mode")
@click.option("-n", default=1, help="Number of parallel connections to make")
def main(endpoint: str, n: int) -> None:
    asyncio.run(run_async_tests_parallel(endpoint, n))


async def run_async_tests_parallel(endpoint: str, n: int) -> None:
    async with aiohttp.ClientSession(endpoint, cookie_jar=aiohttp.CookieJar()) as session:
        async with session.post("/login", data={"username": "admin", "password": "admin"}): pass
        tasks = []
        for i in range(n):
            tasks.append(run_async_tests(session, i))
        await asyncio.gather(*tasks)


async def run_async_tests(session: aiohttp.ClientSession, idx: int) -> None:
    try:
        await asyncio.sleep(1.0 * idx)
        async with session.ws_connect("/assignment/1/websocket") as ws:
            client = DebugClient(ws)
            async with report_time(f"{idx} start"):
                assert (await client.start(EXAMPLE_SOURCE, [1]))
                await client.wait_until_stopped()

            while True:
                await asyncio.sleep(1.0)
                async with report_time(f"{idx} step"):
                    await client.step()
                is_paused = await client.wait_until_stopped()
                if not is_paused:
                    break
    except Exception as e:
        print(e)


if __name__ == "__main__":
    main()
