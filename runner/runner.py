import asyncio.subprocess
import pathlib
import shutil
import signal
import tempfile
from collections import namedtuple
from typing import Optional

from runner import gdbmi
from runner.settings import root, config

CompilationResult = namedtuple("CompilationResult", ["successful", "stdout", "stderr"])


class RunningProgram:
    workdir: pathlib.Path
    gdb: Optional[asyncio.subprocess.Process]
    arch: str
    breakpoints: dict[int, int]
    is_running: bool
    gdb_responses: asyncio.Queue

    def __init__(self):
        self.workdir = pathlib.Path(tempfile.mkdtemp(prefix="asmwebide_runner_"))
        self.gdb = None
        self.arch = "unknown"
        self.breakpoints = {}
        self.is_running = False
        self.gdb_responses = asyncio.Queue()

    @property
    def source_path(self):
        return self.workdir / "source.S"

    @property
    def executable_path(self):
        return self.workdir / "a.out"

    @property
    def stdin_path(self):
        return self.workdir / "input"

    async def compile(self, source_code, arch="x86_64"):
        self.arch = arch
        with open(self.source_path, "w") as f:
            f.write(source_code)

        command = [
            config.archs[arch].gcc,
            "-no-pie",
            "-nodefaultlibs",
            "-nostartfiles",
            "-g",
            "-Wl,--entry=_start_seccomp",
            root / "environment" / "seccomp" / arch / "entry.S",
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

    def set_stdin(self, data: str):
        with open(self.stdin_path, "w") as f:
            f.write(data)

    async def start_gdb(self):
        command = [
            config.archs[self.arch].gdb,
            "-q", "-nx",
            "--interpreter=mi2"
        ]

        self.gdb = await asyncio.subprocess.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

    async def attach_program(self):
        await self.gdb_command(f"-file-exec-and-symbols {self.executable_path}")
        await self.gdb_command(f"-exec-arguments >&2 <{self.stdin_path}")

    async def start_program(self):
        await self.gdb_command(f"-exec-run")

    async def add_breakpoint(self, line):
        if line in self.breakpoints:
            return
        result = await self.gdb_command(f"-break-insert --source {self.source_path} --line {line}")
        if result.status != "done":
            raise ValueError(f"Invalid breakpoint: {result.values['msg']}")
        self.breakpoints[line] = int(result.values["bkpt"]["number"])

    async def remove_breakpoint(self, line):
        if line not in self.breakpoints:
            return
        breakpoint_id = self.breakpoints[line]
        del self.breakpoints[line]

        await self.gdb_command(f"-break-delete {breakpoint_id}")

    async def set_register_value(self, reg, value):
        if reg not in config.archs[self.arch].display_registers:
            raise ValueError("Invalid register")
        try:
            value = int(value, base=0)
        except ValueError:
            raise ValueError("Invalid value")
        await self.gdb_command(f"-gdb-set ${reg}={value}")

    async def gdb_command(self, cmd) -> gdbmi.Result:
        if self.is_running:
            need_resume = True
            self.gdb_interrupt()
        else:
            need_resume = False

        self.gdb.stdin.write(f"{cmd}\n".encode())
        result = await self.gdb_responses.get()

        if need_resume:
            self.gdb.stdin.write("-exec-continue\n".encode())
            await self.gdb_responses.get()

        return result

    def gdb_interrupt(self):
        self.gdb.send_signal(signal.SIGINT)

    async def terminate(self):
        if self.running:
            self.gdb_interrupt()
            self.gdb.stdin.write("-gdb-exit\n".encode())
            await self.gdb.wait()
            self.gdb = None

    async def close(self):
        await self.terminate()
        shutil.rmtree(self.workdir)

    async def gdb_events_iterator(self):
        while self.running:
            line = await self.gdb.stdout.readline()
            if not line:
                break
            gdb_response = gdbmi.parse_gdb_response(line.decode())
            if gdb_response is None:
                continue

            if type(gdb_response) is gdbmi.ExecAsync:
                self.is_running = gdb_response.status == "running"

            if type(gdb_response) is gdbmi.Result:
                if gdb_response.status == "exit":
                    break
                await self.gdb_responses.put(gdb_response)
            else:
                yield gdb_response

    async def program_output_iterator(self):
        while self.running:
            line = await self.gdb.stderr.readline()
            if not line:
                break
            yield line.decode(errors="replace")

    async def get_register_values(self):
        regs = config.archs[self.arch].display_registers
        result = await self.gdb_command("-data-list-register-names")
        reg_name_to_id = {}
        for reg_id, reg_name in enumerate(result.values["register-names"]):
            reg_name_to_id[reg_name] = reg_id
        reg_ids = []
        for reg_name in regs:
            reg_ids.append(reg_name_to_id[reg_name])

        result = await self.gdb_command(f"-data-list-register-values N {' '.join(map(str, reg_ids))}")
        reg_mapping = []
        for val, reg in zip(result.values["register-values"], regs):
            reg_mapping.append([reg, val["value"]])
        return reg_mapping

    @property
    def running(self):
        return self.gdb is not None
