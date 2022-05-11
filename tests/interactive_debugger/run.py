#!/usr/bin/env python3

import asyncio
from contextlib import asynccontextmanager
import time
from typing import List
import aiohttp
import click


EXAMPLE_SOURCE_X86_64 = r"""
mov $30, %rax

again:
dec %rax
test %rax, %rax
jz end
jmp again

end: nop
"""

EXAMPLE_SOURCE_AVR = r"""
ldi r16, 30

again:
cpi r16, 0
breq end
subi r16, 1
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
            "sample_test": None,
            "watch": []
        })
        data = await self.ws.receive_json()
        assert data["type"] == "compilation_result"
        return data["successful"]

    async def wait_until_stopped(self) -> bool:
        while True:
            data = await self.ws.receive_json()
            if data["type"] == "paused":
                if data["line"] >= 9:
                    return False
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
@click.option("--arch", default="x86_64")
def main(endpoint: str, n: int, arch: str) -> None:
    asyncio.run(run_async_tests_parallel(endpoint, n, arch))


async def run_async_tests_parallel(endpoint: str, n: int, arch: str) -> None:
    async with aiohttp.ClientSession(endpoint, cookie_jar=aiohttp.CookieJar()) as session:
        async with session.post("/login", data={"username": "admin", "password": "admin"}): pass
        tasks = []
        for i in range(n):
            tasks.append(run_async_tests(session, i, arch))
        await asyncio.gather(*tasks)


async def run_async_tests(session: aiohttp.ClientSession, idx: int, arch: str) -> None:
    try:
        await asyncio.sleep(1.0 * idx)
        assignment = 1 if arch == "x86_64" else 2
        source = EXAMPLE_SOURCE_X86_64 if arch == "x86_64" else EXAMPLE_SOURCE_AVR
        async with session.ws_connect(f"/assignment/{assignment}/websocket") as ws:
            client = DebugClient(ws)
            async with report_time(f"{idx} start"):
                assert (await client.start(source, [1]))
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
