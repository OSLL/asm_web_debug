#!/usr/bin/env python3

import asyncio
import random
import time
import traceback
from typing import List
import aiohttp
import click


EXAMPLE_SOURCE = r"""
nop
again: jmp again
"""

ASSIGNMENTS = {
    "x86_64": 1,
    "avr5": 2
}

REGISTERS = {
    "x86_64": [ ("rax", 64), ("rbx", 64), ("rdi", 64), ("rsi", 64) ],
    "avr5": [ ("r16", 8), ("r17", 8), ("r18", 8), ("r19", 8) ]
}


class DebugClient:
    ws: aiohttp.ClientWebSocketResponse
    arch: str
    idx: int

    def __init__(self, ws: aiohttp.ClientWebSocketResponse, arch: str, idx: int) -> None:
        self.ws = ws
        self.arch = arch
        self.idx = idx

    async def start(self, source_code: str, breakpoints: List[int]) -> None:
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
        assert data["successful"]
        metadata = await self.ws.receive_json()
        assert metadata["type"] == "metadata"
        for k, v in sorted(metadata["data"].items()):
            print(f"{self.idx}\t{k}\t{v}")

    async def wait_until_stopped(self) -> None:
        while True:
            data = await self.ws.receive_json()
            if data["type"] == "error":
                print(data)
                raise RuntimeError()
            if data["type"] in ["paused", "finished"]:
                return

    async def wait_for_registers(self) -> None:
        while True:
            data = await self.ws.receive_json()
            if data["type"] in ["registers"]:
                return

    async def request_registers(self) -> None:
        await self.ws.send_json({"type": "get_registers"})

    async def action_next_step(self):
        now = time.monotonic()
        await self.ws.send_json({"type": "step_over"})
        await self.wait_until_stopped()
        print(f"{self.idx}\tnext_step\t{time.monotonic() - now}")

    async def action_continue(self):
        await self.ws.send_json({
            "type": "add_breakpoint",
            "line": 3
        })

        now = time.monotonic()
        await self.ws.send_json({"type": "continue"})
        await self.wait_until_stopped()
        print(f"{self.idx}\tcontinue\t{time.monotonic() - now}")

        await self.ws.send_json({
            "type": "remove_breakpoint",
            "line": 3
        })

    async def action_set_register_value(self):
        reg, bits = random.choice(REGISTERS[self.arch])
        value = random.randrange(2**(bits - 1))
        now = time.monotonic()
        await self.ws.send_json({
            "type": "update_register",
            "reg": reg,
            "value": str(value)
        })
        await self.wait_for_registers()
        print(f"{self.idx}\tset_register_value\t{time.monotonic() - now}")

    async def profile_stop_immediately(self):
        pass

    async def profile_single_step(self):
        while True:
            await asyncio.sleep(random.random())
            await random.choice([
                self.action_next_step,
                self.action_set_register_value,
                self.action_continue
            ])()

    async def profile_busy_loop(self):
        while True:
            await asyncio.sleep(random.random())
            await self.ws.send_json({"type": "continue"})
            await asyncio.sleep(random.random())
            await self.ws.send_json({"type": "pause"})
            await self.wait_until_stopped()


@click.command()
@click.option("--endpoint", default="http://localhost:8080", help="Endpoint for ASM WEB IDE launched in test mode")
@click.option("-n", default=1, help="Number of parallel connections to make")
@click.option("--delay", default=1.0)
@click.option("--arch", default="x86_64")
@click.option("--profile", default="SingleStep")
def main(**kwargs) -> None:
    asyncio.run(run_async_tests_parallel(**kwargs))


async def run_async_tests_parallel(endpoint: str, n: int, arch: str, profile: str, delay: float) -> None:
    print("idx\tmeasurement\tvalue")
    async with aiohttp.ClientSession(endpoint, cookie_jar=aiohttp.CookieJar()) as session:
        async with session.post("/login", data={"username": "admin", "password": "admin"}): pass
        tasks = []
        for i in range(n):
            tasks.append(run_async_tests(session, i, arch, profile, delay))
        await asyncio.gather(*tasks)


async def run_async_tests(session: aiohttp.ClientSession, idx: int, arch: str, profile: str, delay: float) -> None:
    try:
        await asyncio.sleep(delay * idx)
        assignment = ASSIGNMENTS[arch]
        source = EXAMPLE_SOURCE
        async with session.ws_connect(f"/assignment/{assignment}/websocket") as ws:
            client = DebugClient(ws, arch, idx)
            now = time.monotonic()
            await client.start(source, [1])
            await client.wait_until_stopped()
            print(f"{idx}\ttotal_time\t{time.monotonic() - now}")

            if profile == "StopImmediately":
                await client.profile_stop_immediately()
            if profile == "SingleStep":
                await client.profile_single_step()
            if profile == "BusyLoop":
                await client.profile_busy_loop()
    except Exception:
        traceback.print_exc()


if __name__ == "__main__":
    main()
