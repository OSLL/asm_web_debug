import asyncio
import json
from typing import Dict, Optional, List

from aiohttp import web, WSMsgType

from runner import gdbmi
from runner.debugger import DebuggerError
from runner.runner import BreakpointId, RunningProgram
from runner.settings import config


async def run_interactor(ws: web.WebSocketResponse):
    interactor = WSInteractor(ws)
    try:
        await interactor.run()
    finally:
        await interactor.close()


class WSInteractor:
    ws: web.WebSocketResponse
    running_program: Optional[RunningProgram]
    breakpoints: Dict[int, BreakpointId]

    def __init__(self, ws: web.WebSocketResponse):
        self.ws = ws
        self.running_program = None
        self.breakpoints = {}

    async def handle_incoming_messages(self):
        async for msg in self.ws:
            if msg.type != WSMsgType.TEXT:
                break
            try:
                json_msg = json.loads(msg.data)
                await self.handle_message(json_msg)
            except (ValueError, DebuggerError) as e:
                await self.ws.send_json({
                    "type": "errror",
                    "message": str(e)
                })

    async def start_program(self, source: str, stdin: str, breakpoints: List[int]):
        if self.running_program:
            await self.running_program.close()
        self.breakpoints = {}
        self.running_program = RunningProgram("x86_64")
        result = await self.running_program.compile(source)
        await self.ws.send_json({
            "type": "compilation_result",
            "successful": result.successful,
            "stdout": result.stdout,
            "stderr": result.stderr
        })

        if not result.successful:
            return

        self.running_program.set_stdin(stdin)
        await self.running_program.start_debugger()
        asyncio.create_task(self.handle_gdb_events())

        for line in breakpoints:
            self.breakpoints[line] = await self.running_program.add_breakpoint(line)

        await self.running_program.start_program()

    async def terminate_program(self):
        await self.close()
        await self.ws.send_json({
            "type": "finished"
        })

    async def send_registers_state(self):
        registers = await self.running_program.get_register_values(config.archs[self.running_program.arch].display_registers)
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

        if not self.running_program:
            return

        if msg["type"] == "kill":
            await self.terminate_program()

        if msg["type"] == "continue":
            await self.running_program.continue_execution()

        if msg["type"] == "pause":
            await self.running_program.interrupt_execution()

        if msg["type"] == "step_into":
            await self.running_program.step_into()

        if msg["type"] == "step_over":
            await self.running_program.step_over()

        if msg["type"] == "step_out":
            await self.running_program.step_out()

        if msg["type"] == "add_breakpoint":
            line = msg.get("line")
            if type(line) is not int:
                raise ValueError("Expected 'line' to be int")
            await self.running_program.add_breakpoint(line)

        if msg["type"] == "remove_breakpoint":
            line = msg.get("line")
            if type(line) is not int:
                raise ValueError("Expected 'line' to be int")
            if line not in self.breakpoints:
                raise ValueError("Invalid breakpoint")
            breakpoint_id = self.breakpoints[line]
            del self.breakpoints[line]
            await self.running_program.remove_breakpoint(breakpoint_id)

        if msg["type"] == "get_registers":
            await self.send_registers_state()

        if msg["type"] == "update_register":
            reg = msg.get("reg")
            if reg not in config.archs[self.running_program.arch].display_registers:
                raise ValueError("Expected 'reg' to be a valid register")
            value = msg.get("value")
            if type(value) is not str:
                raise ValueError("Expected 'value' to be a string")
            await self.running_program.set_register_value(reg, value)
            await self.send_registers_state()

    async def handle_gdb_events(self):
        async for event in self.running_program.debugger.gdb_notifications_iterator():
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

            if type(event) is gdbmi.TargetOutput:
                await self.ws.send_json({
                    "type": "output",
                    "data": event.line
                })

    async def run(self):
        await self.handle_incoming_messages()

    async def close(self):
        if self.running_program:
            await self.running_program.close()
            self.running_program = None
