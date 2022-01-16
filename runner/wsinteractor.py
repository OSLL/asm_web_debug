import asyncio
import base64
import json
from typing import Optional, List

from aiohttp import web, WSMsgType

from runner import gdbmi
from runner.runner import RunningProgram


async def run_interactor(ws: web.WebSocketResponse):
    interactor = WSInteractor(ws)
    try:
        await interactor.run()
    finally:
        await interactor.close()


class WSInteractor:
    ws: web.WebSocketResponse
    runner: Optional[RunningProgram]

    def __init__(self, ws: web.WebSocketResponse):
        self.ws = ws
        self.runner = None

    async def handle_incoming_messages(self):
        async for msg in self.ws:
            if msg.type != WSMsgType.TEXT:
                break
            try:
                json_msg = json.loads(msg.data)
                await self.handle_message(json_msg)
            except ValueError as e:
                await self.ws.send_json({
                    "type": "errror",
                    "message": str(e)
                })

    async def start_program(self, source: str, stdin: str, breakpoints: List[int]):
        if self.runner:
            await self.runner.close()
        self.runner = RunningProgram()
        result = await self.runner.compile(source, "x86_64")
        await self.ws.send_json({
            "type": "compilation_result",
            "successful": result.successful,
            "stdout": result.stdout,
            "stderr": result.stderr
        })

        if not result.successful:
            return

        self.runner.set_stdin(stdin)
        await self.runner.start_gdb()
        asyncio.create_task(self.handle_gdb_events())
        asyncio.create_task(self.handle_program_output())

        await self.runner.attach_program()
        for line in breakpoints:
            await self.runner.add_breakpoint(line)
        await self.runner.start_program()

    async def terminate_program(self):
        if self.runner:
            await self.runner.close()
            self.runner = None
            await self.ws.send_json({
                "type": "finished"
            })

    async def send_registers_state(self):
        registers = await self.runner.get_register_values()
        await self.ws.send_json({
            "type": "registers",
            "data": registers
        })

    async def handle_message(self, msg):
        if type(msg) is not dict:
            raise ValueError("Expected a dict")
        if type(msg.get("type")) is not str:
            raise ValueError("Expected 'type' field to be a string")

        if msg["type"] == "run":
            source = msg.get("source")
            if type(source) is not str:
                raise ValueError("Expected 'source' field to be a string")
            stdin = msg.get("input")
            if type(stdin) is not str:
                raise ValueError("Expected 'input' field to be a string")
            breakpoints = msg.get("breakpoints")
            if type(breakpoints) is not list:
                raise ValueError("Expected 'breakpoints' field to be a list")
            for b in breakpoints:
                if type(b) is not int:
                    raise ValueError("Expected 'breakpoints' contents to be ints")
            await self.start_program(source, stdin, breakpoints)

        if not self.runner:
            return

        if msg["type"] == "kill":
            await self.terminate_program()

        if msg["type"] == "continue":
            await self.runner.gdb_command("-exec-continue")

        if msg["type"] == "pause":
            self.runner.gdb_interrupt()

        if msg["type"] == "step_into":
            await self.runner.gdb_command("-exec-next-instruction")

        if msg["type"] == "step_over":
            await self.runner.gdb_command("-exec-step-instruction")

        if msg["type"] == "step_out":
            await self.runner.gdb_command("-exec-finish")

        if msg["type"] == "add_breakpoint":
            line = msg.get("line")
            if type(line) is not int:
                raise ValueError("Expected 'line' to be int")
            await self.runner.add_breakpoint(line)

        if msg["type"] == "remove_breakpoint":
            line = msg.get("line")
            if type(line) is not int:
                raise ValueError("Expected 'line' to be int")
            await self.runner.remove_breakpoint(line)

        if msg["type"] == "get_registers":
            await self.send_registers_state()

        if msg["type"] == "update_register":
            reg = msg.get("reg")
            if type(reg) is not str:
                raise ValueError("Expected 'reg' to be a string")
            value = msg.get("value")
            if type(value) is not str:
                raise ValueError("Expected 'value' to be a string")
            await self.runner.set_register_value(reg, value)
            await self.send_registers_state()

    async def handle_gdb_events(self):
        async for event in self.runner.gdb_events_iterator():
            if type(event) is gdbmi.ExecAsync:
                if event.status == "running":
                    await self.ws.send_json({
                        "type": "running"
                    })
                elif event.status == "stopped" and event.values["reason"].startswith("exited"):
                    if event.values["reason"] == "exited-signalled":
                        signal_name = event.values["signal-name"]
                        status = f"\n[process received signal {signal_name}]"
                    else:
                        exitcode = int(event.values.get("exit-code", "0"), 8)
                        status = f"\n[process exited with exit code {exitcode}]"
                    await self.terminate_program()
                    await self.ws.send_json({
                        "type": "output",
                        "data": status
                    })
                elif event.status == "stopped" and event.values["reason"] in ["breakpoint-hit", "end-stepping-range", "function-finished", "location-reached", "signal-received"]:
                    await self.ws.send_json({
                        "type": "paused",
                        "line": int(event.values["frame"]["line"])
                    })

    async def handle_program_output(self):
        async for output in self.runner.program_output_iterator():
            await self.ws.send_json({
                "type": "output",
                "data": output
            })

    async def run(self):
        await self.handle_incoming_messages()

    async def close(self):
        if self.runner:
            await self.runner.close()
            self.runner = None
