import asyncio
import json
import logging
import time
import traceback
from typing import Dict, Optional, List, Type

from aiohttp import web, WSMsgType
import aiohttp
from multidict import MultiDict

from runner import gdbmi
from runner.checkerlib import BaseChecker, Checker, CheckerException
from runner.debugger import DebuggerError
from runner.runner import BreakpointId, DebugSession
from runner.settings import config


_flask_session: Optional[aiohttp.ClientSession] = None

def get_flask_session() -> aiohttp.ClientSession:
    global _flask_session
    if not _flask_session:
        _flask_session = aiohttp.ClientSession(base_url="http://web")
    return _flask_session


async def run_interactor(ws: web.WebSocketResponse, query: MultiDict[str]):
    interactor = WSInteractor(ws, query)
    try:
        await interactor.run()
    finally:
        await interactor.close_and_post_stats()


class WSInteractor:
    ws: web.WebSocketResponse
    debug_session: Optional[DebugSession]
    breakpoints: Dict[int, BreakpointId]
    watch: List[str]
    checker_name: Optional[str]
    checker_class: Optional[Type[Checker]]
    user_id: int
    assignment_id: int
    metadata: dict
    handle_gdb_events_task: Optional[asyncio.Task]
    uninterrupted_timeout_task: Optional[asyncio.Task]
    closed: bool
    arch: str

    def __init__(self, ws: web.WebSocketResponse, query: MultiDict[str]):
        self.ws = ws
        self.debug_session = None
        self.breakpoints = {}
        self.watch = []
        self.checker_name = query.get("checker_name")
        self.checker_class = BaseChecker._all_checkers.get(self.checker_name)
        self.user_id = int(query.get("user_id"))
        self.assignment_id = int(query.get("assignment_id"))
        self.metadata = {}
        self.handle_gdb_events_task = None
        self.uninterrupted_timeout_task = None
        self.closed = True
        self.arch = query.get("arch")

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

    async def start_program(self, source: str, breakpoints: List[int], sample_test: Optional[str], watch: List[str]):
        if self.debug_session:
            await self.terminate_program()

        self.breakpoints = {}
        self.watch = watch
        self.debug_session = DebugSession(self.arch)
        self.metadata = {
            "source_code": source,
            "arch": self.debug_session.arch,
            "user_id": self.user_id,
            "assignment_id": self.assignment_id,
            "started_at": time.time()
        }

        result = await self.debug_session.compile(source)
        await self.ws.send_json({
            "type": "compilation_result",
            "successful": result.successful,
            "stdout": result.stdout,
            "stderr": result.stderr
        })

        if not result.successful:
            return

        await self.debug_session.start_debugger(real_time_limit=config.default_online_real_time_limit)

        await self.post_stats()

        for line in breakpoints:
            self.breakpoints[line] = await self.debug_session.add_breakpoint(line)

        if self.checker_class and sample_test:
            checker = self.checker_class(arch=self.debug_session.arch, source_code=source)
            checker.sample_test = sample_test
            checker.program = self.debug_session
            await self.debug_session.restart()
            await checker.prepare_sample_test()
            await self.debug_session.continue_execution()
        else:
            await self.debug_session.start_program()

        self.handle_gdb_events_task = asyncio.create_task(self.handle_gdb_events())

    async def post_stats(self):
        if not self.debug_session:
            return

        try:
            data = {
                "cpu_time_used": await self.debug_session.get_total_cpu_time_used(),
                "memory_used": await self.debug_session.get_max_memory_used()
            }
        except DebuggerError:
            data = {
                "cpu_time_used": None,
                "memory_used": None
            }

        data.update(self.metadata)

        try:
            async with get_flask_session().post("/internal/debug_session_info", json=data) as resp:
                self.metadata.update(await resp.json())
        except aiohttp.ClientError:
            pass

    async def close_and_post_stats(self):
        try:
            self.metadata["finished_at"] = time.time()
            await self.post_stats()
        finally:
            self.close()

    async def terminate_program(self):
        if self.uninterrupted_timeout_task:
            self.uninterrupted_timeout_task.cancel()
            self.uninterrupted_timeout_task = None
        await self.ws.send_json({
            "type": "finished"
        })
        await self.close_and_post_stats()

    async def send_registers_state(self):
        data = await self.debug_session.get_register_values(config.archs[self.debug_session.arch].display_registers)
        registers = []

        for reg, val in data:
            if reg == "eflags":
                registers.append((reg, val, val, val))
            else:
                bits = 64
                signed = int(val, 0)
                unsigned = signed % (2 ** bits)
                hexval = hex(unsigned)
                registers.append((reg, str(signed), str(unsigned), str(hexval)))

        await self.ws.send_json({
            "type": "registers",
            "data": registers
        })

    async def send_watch_state(self):
        data = []
        for expr in self.watch:
            try:
                value = await self.debug_session.evaluate_expression(expr)
            except DebuggerError:
                continue
            data.append((expr, value))

        await self.ws.send_json({
            "type": "watch",
            "data": data
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
            breakpoints = msg.get("breakpoints")
            if type(breakpoints) is not list:
                raise ValueError("Expected 'breakpoints' field to be a list")
            for b in breakpoints:
                if type(b) is not int:
                    raise ValueError("Expected 'breakpoints' contents to be ints")
            sample_test = msg.get("sample_test")
            if sample_test is not None and type(sample_test) is not str:
                raise ValueError("Expected 'sample_test' to be either null or a string")
            watch = msg.get("watch")
            if type(watch) is not list:
                raise ValueError("Expected 'watch' field to be a list")
            for w in watch:
                if type(w) is not str:
                    raise ValueError("Expected 'watch' contents to be strings")

            if self.checker_class is not None:
                source = self.checker_class(arch=self.arch, source_code=source).get_source_for_interactive_debugger()
            await self.start_program(source, breakpoints, sample_test, watch)

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

        if msg["type"] == "add_watch":
            expr = msg.get("expr")
            if type(expr) is not str:
                raise ValueError("Expected 'expr' to be a string")
            expr = expr.strip()
            if expr in self.watch:
                return
            try:
                await self.debug_session.evaluate_expression(expr)
            except DebuggerError:
                return
            self.watch.append(expr)
            await self.send_watch_state()

        if msg["type"] == "remove_watch":
            expr = msg.get("expr")
            if type(expr) is not str:
                raise ValueError("Expected 'expr' to be a string")
            expr = expr.strip()
            self.watch.remove(expr)
            await self.send_watch_state()

        if msg["type"] == "get_registers":
            await self.send_registers_state()
            await self.send_watch_state()

        if msg["type"] == "update_register":
            reg = msg.get("reg")
            if reg not in config.archs[self.debug_session.arch].display_registers:
                raise ValueError("Expected 'reg' to be a valid register")
            value = msg.get("value")
            if type(value) is not str:
                raise ValueError("Expected 'value' to be a string")
            try:
                value = int(value.strip(), 0)
            except ValueError:
                raise ValueError("Expected register value to be a valid integer")
            await self.debug_session.set_register_value(reg, str(value))
            await self.send_registers_state()
            await self.send_watch_state()

    async def send_output(self, output: str) -> None:
        await self.ws.send_json({
            "type": "output",
            "data": output
        })

    async def terminate_after_timeout(self, timeout: float) -> None:
        await asyncio.sleep(timeout)
        await self.send_output(f"[terminated after {timeout} seconds of inactivity]")
        await self.terminate_program()

    async def handle_gdb_events(self):
        try:
            async for event in self.debug_session.debugger.gdb_notifications_iterator():
                if type(event) is gdbmi.ExecAsync:
                    if event.status == "running":
                        await self.ws.send_json({
                            "type": "running"
                        })
                        self.uninterrupted_timeout_task = asyncio.create_task(
                            self.terminate_after_timeout(config.default_uninterrupted_real_time_limit))
                        continue

                    if self.uninterrupted_timeout_task:
                        self.uninterrupted_timeout_task.cancel()
                        self.uninterrupted_timeout_task = None

                    if event.status == "stopped":
                        reason = event.values.get("reason")
                        if not reason:
                            continue
                        if reason.startswith("exited"):
                            if reason == "exited-signalled":
                                signal_name = event.values["signal-name"]
                                status = f"[process received signal {signal_name}]"
                            else:
                                exitcode = int(event.values.get("exit-code", "0"), 8)
                                status = f"[process exited with exit code {exitcode}]"
                            await self.send_output(status)
                            await self.terminate_program()
                        if reason in ["breakpoint-hit", "end-stepping-range", "function-finished", "location-reached", "signal-received"]:
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
        except Exception:
            logging.error(traceback.format_exc())
            await self.terminate_program()

    async def run(self):
        await self.handle_incoming_messages()

    def close(self):
        if self.uninterrupted_timeout_task:
            self.uninterrupted_timeout_task.cancel()
            self.uninterrupted_timeout_task = None
        if self.handle_gdb_events_task:
            self.handle_gdb_events_task.cancel()
            self.handle_gdb_events_task = None
        if self.debug_session:
            self.debug_session.close()
            self.debug_session = None
            self.metadata = {}
