import asyncio
import json
from typing import Dict, Optional, List, Type

from aiohttp import web, WSMsgType

from runner import gdbmi
from runner.checkerlib import BaseChecker, Checker, CheckerException
from runner.debugger import DebuggerError
from runner.runner import BreakpointId, DebugSession
from runner.settings import config


async def run_interactor(ws: web.WebSocketResponse):
    interactor = WSInteractor(ws)
    try:
        await interactor.run()
    finally:
        await interactor.close()


class WSInteractor:
    ws: web.WebSocketResponse
    debug_session: Optional[DebugSession]
    breakpoints: Dict[int, BreakpointId]

    def __init__(self, ws: web.WebSocketResponse):
        self.ws = ws
        self.debug_session = None
        self.breakpoints = {}

    async def handle_incoming_messages(self):
        async for msg in self.ws:
            if msg.type != WSMsgType.TEXT:
                break
            try:
                json_msg = json.loads(msg.data)
                await self.handle_message(json_msg)
            except (ValueError, DebuggerError, CheckerException) as e:
                await self.ws.send_json({
                    "type": "error",
                    "message": str(e)
                })

    async def start_program(self, source: str, stdin: str, breakpoints: List[int], checker_class: Optional[Type[Checker]], sample_test: Optional[str]):
        if self.debug_session:
            await self.debug_session.close()
        self.breakpoints = {}
        self.debug_session = DebugSession("x86_64")
        result = await self.debug_session.compile(source)
        await self.ws.send_json({
            "type": "compilation_result",
            "successful": result.successful,
            "stdout": result.stdout,
            "stderr": result.stderr
        })

        if not result.successful:
            return

        self.debug_session.set_stdin(stdin)
        await self.debug_session.start_debugger()

        for line in breakpoints:
            self.breakpoints[line] = await self.debug_session.add_breakpoint(line)

        if checker_class and sample_test:
            checker = checker_class(arch=self.debug_session.arch, source_code=source)
            checker.sample_test = sample_test
            checker.program = self.debug_session
            await self.debug_session.restart()
            await checker.prepare_sample_test()
            await self.debug_session.continue_execution()
        else:
            await self.debug_session.start_program()

        asyncio.create_task(self.handle_gdb_events())

    async def terminate_program(self):
        await self.ws.send_json({
            "type": "finished"
        })
        await self.close()

    async def send_registers_state(self):
        registers = await self.debug_session.get_register_values(config.archs[self.debug_session.arch].display_registers)
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
            sample_test = msg.get("sample_test")
            if sample_test is not None and type(sample_test) is not str:
                raise ValueError("Expected 'sample_test' to be either null or a string")
            checker_name = msg.get("checker_name")
            checker_class = BaseChecker._all_checkers.get(checker_name)
            if checker_class is not None:
                source = checker_class(arch="x86_64", source_code=source).get_source_for_interactive_debugger()
            await self.start_program(source, stdin, breakpoints, checker_class, sample_test)

        if not self.debug_session:
            return

        if msg["type"] == "kill":
            await self.terminate_program()

        if msg["type"] == "continue":
            await self.debug_session.continue_execution()

        if msg["type"] == "pause":
            await self.debug_session.interrupt_execution()

        if msg["type"] == "step_into":
            await self.debug_session.step_into()

        if msg["type"] == "step_over":
            await self.debug_session.step_over()

        if msg["type"] == "step_out":
            await self.debug_session.step_out()

        if msg["type"] == "add_breakpoint":
            line = msg.get("line")
            if type(line) is not int:
                raise ValueError("Expected 'line' to be int")
            await self.debug_session.add_breakpoint(line)

        if msg["type"] == "remove_breakpoint":
            line = msg.get("line")
            if type(line) is not int:
                raise ValueError("Expected 'line' to be int")
            if line not in self.breakpoints:
                raise ValueError("Invalid breakpoint")
            breakpoint_id = self.breakpoints[line]
            del self.breakpoints[line]
            await self.debug_session.remove_breakpoint(breakpoint_id)

        if msg["type"] == "get_registers":
            await self.send_registers_state()

        if msg["type"] == "update_register":
            reg = msg.get("reg")
            if reg not in config.archs[self.debug_session.arch].display_registers:
                raise ValueError("Expected 'reg' to be a valid register")
            value = msg.get("value")
            if type(value) is not str:
                raise ValueError("Expected 'value' to be a string")
            await self.debug_session.set_register_value(reg, value)
            await self.send_registers_state()

    async def send_output(self, output: str) -> None:
        await self.ws.send_json({
            "type": "output",
            "data": output
        })

    async def handle_gdb_events(self):
        async for event in self.debug_session.debugger.gdb_notifications_iterator():
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
                    await self.send_output(status)
                    await self.terminate_program()
                elif event.status == "stopped" and event.values["reason"] in ["breakpoint-hit", "end-stepping-range", "function-finished", "location-reached", "signal-received"]:
                    if "line" in event.values["frame"]:
                        line = int(event.values["frame"]["line"])
                    else:
                        line = -1
                    await self.ws.send_json({
                        "type": "paused",
                        "line": line
                    })

            if type(event) is gdbmi.TargetOutput:
                await self.send_output(event.line)

    async def run(self):
        await self.handle_incoming_messages()

    async def close(self):
        if self.debug_session:
            await self.debug_session.close()
            self.debug_session = None
