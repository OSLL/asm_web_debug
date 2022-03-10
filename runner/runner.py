import asyncio.subprocess
import binascii
from dataclasses import dataclass
import pathlib
import shutil
import tempfile
from collections import namedtuple
from typing import Any, Callable, Dict, Iterable, List, Optional, Tuple, Type, TypeAlias

from runner import gdbmi
from runner.debugger import Debugger
from runner.settings import root, config

CompilationResult = namedtuple("CompilationResult", ["successful", "stdout", "stderr"])


BreakpointId: TypeAlias = int
RegisterName: TypeAlias = str


class RunningProgram:
    workdir: pathlib.Path
    arch: str
    debugger: Debugger
    reg_name_to_id: Optional[Dict[RegisterName, int]]
    event_subscribers: List[Callable[[gdbmi.AnyNotification], None]]

    def __init__(self, arch: str) -> None:
        self.workdir = pathlib.Path(tempfile.mkdtemp(prefix="asmwebide_runner_"))
        self.arch = arch
        self.debugger = Debugger()
        self.reg_name_to_id = None
        self.set_stdin("")
        self.exception_on_stop = None
        self.event_subscribers = []

    @property
    def source_path(self) -> pathlib.Path:
        return self.workdir / "source.S"

    @property
    def executable_path(self) -> pathlib.Path:
        return self.workdir / "a.out"

    @property
    def stdin_path(self) -> pathlib.Path:
        return self.workdir / "input"

    async def compile(self, source_code) -> CompilationResult:
        with open(self.source_path, "w") as f:
            f.write(source_code)

        command = [
            config.archs[self.arch].gcc,
            "-no-pie",
            "-nodefaultlibs",
            "-nostartfiles",
            "-g",
            "-Wl,--entry=_start_seccomp",
            root / "environment" / "seccomp" / self.arch / "entry.S",
            self.source_path,
            "-o", self.executable_path
        ]

        process = await asyncio.subprocess.create_subprocess_exec(
            *command,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        return CompilationResult(
            successful=process.returncode == 0,
            stdout=stdout.decode(),
            stderr=stderr.decode()
        )

    def set_stdin(self, data: str) -> None:
        with open(self.stdin_path, "w") as f:
            f.write(data)

    async def start_debugger(self) -> None:
        await self.debugger.start(config.archs[self.arch].gdb)
        await self.debugger.gdb_command(f"-gdb-set mi-async on")
        await self.debugger.gdb_command(f"-file-exec-and-symbols {self.executable_path}")
        await self.debugger.gdb_command(f"-exec-arguments >&2 <{self.stdin_path}")

    async def terminate(self) -> None:
        if self.debugger is not None:
            await self.debugger.terminate()

    async def close(self) -> None:
        await self.terminate()
        shutil.rmtree(self.workdir)

    async def start_program(self) -> None:
        await self.debugger.gdb_command(f"-exec-run")

    async def add_breakpoint(self, line_or_function: int | str) -> BreakpointId:
        if type(line_or_function) is int:
            cmd = f"-break-insert --source {self.source_path} --line {line_or_function}"
        else:
            cmd = f"-break-insert --source {self.source_path} --function {line_or_function}"
        result = await self.debugger.gdb_command(cmd)
        return int(result["bkpt"]["number"])

    async def remove_breakpoint(self, breakpoint_id: BreakpointId) -> None:
        await self.debugger.gdb_command(f"-break-delete {breakpoint_id}")

    async def set_register_value(self, reg: RegisterName, value: str) -> None:
        await self.debugger.gdb_command(f"-gdb-set ${reg}={value}")

    async def get_register_values(self, regs: Iterable[RegisterName], format: str = "N") -> List[Tuple[RegisterName, str]]:
        if self.reg_name_to_id is None:
            result = await self.debugger.gdb_command("-data-list-register-names")
            self.reg_name_to_id = {}
            for reg_id, reg_name in enumerate(result["register-names"]):
                self.reg_name_to_id[reg_name] = reg_id

        reg_ids = []
        for reg_name in regs:
            reg_ids.append(self.reg_name_to_id[reg_name])

        result = await self.debugger.gdb_command(f"-data-list-register-values {format} {' '.join(map(str, reg_ids))}")
        reg_mapping = []
        for val, reg in zip(result["register-values"], regs):
            reg_mapping.append((reg, val["value"]))
        return reg_mapping

    async def get_register_value(self, reg: RegisterName, format:str = "N") -> str:
        vals = await self.get_register_values([reg])
        if not vals:
            raise ValueError(f"Invalid register: {reg}")
        return vals[0][1]

    async def write_memory_region(self, addr: Any, data: bytes, count: Optional[int] = None) -> None:
        await self.debugger.gdb_command(f"-data-write-memory-bytes {addr} {binascii.hexlify(data).decode()} {count if count is not None else ''}")

    async def read_memory_region(self, addr: Any, count: int) -> bytes:
        gdb_response = await self.debugger.gdb_command(f"-data-read-memory-bytes {addr} {count}")
        result = b""
        for chunk in gdb_response["memory"]:
            result += binascii.unhexlify(chunk["contents"])
        return result

    async def interrupt_execution(self) -> None:
        await self.debugger.gdb_command("-exec-interrupt")

    async def continue_execution(self) -> None:
        await self.debugger.gdb_command("-exec-continue")

    async def step_into(self) -> None:
        await self.debugger.gdb_command("-exec-next-instruction")

    async def step_over(self) -> None:
        await self.debugger.gdb_command("-exec-step-instruction")

    async def step_out(self) -> None:
        await self.debugger.gdb_command("-exec-finish")

    async def wait_until_stopped(self) -> gdbmi.ExecAsync:
        async for event in self.debugger.gdb_notifications_iterator():
            for fn in self.event_subscribers:
                fn(event)
            if type(event) is gdbmi.ExecAsync and event.status == "stopped":
                return event

    async def continue_until(self, line_or_function: int | str) -> None:
        breakpoint_id = await self.add_breakpoint(line_or_function)
        while True:
            await self.continue_execution()
            event = await self.wait_until_stopped()

            if event.values["reason"] == "breakpoint-hit" and event.values["bkptno"] == str(breakpoint_id):
                break
        await self.remove_breakpoint(breakpoint_id)
