import asyncio
import binascii
import pathlib
import shutil
import tempfile
from collections import namedtuple
from typing import Any, Callable, Dict, Iterable, List, Optional, Set, Tuple, Type, TypeAlias
from uuid import uuid4

from runner import docker, gdbmi
from runner.debugger import Debugger, DebuggerError
from runner.settings import root, config

CompilationResult = namedtuple("CompilationResult", ["successful", "stdout", "stderr"])


BreakpointId: TypeAlias = int
RegisterName: TypeAlias = str


active_debug_sessions: Set["DebugSession"] = set()


class DebugSession:
    workdir: pathlib.Path
    arch: str
    debugger: Debugger
    reg_name_to_id: Optional[Dict[RegisterName, int]]
    event_subscribers: List[Callable[[gdbmi.AnyNotification], None]]
    gdbstub_container_id: str
    real_time_limit: Optional[int]

    closed: bool

    def __init__(self, arch: str) -> None:
        self.workdir = pathlib.Path(tempfile.mkdtemp(prefix="asmwebide_runner_", dir=config.runner_data_path))
        self.arch = arch
        self.debugger = Debugger()
        self.reg_name_to_id = None
        self.event_subscribers = []
        self.gdbstub_container_id = ""
        self.closed = False
        self.real_time_limit = None

    @property
    def session_id(self) -> str:
        return self.workdir.name

    @property
    def source_path(self) -> pathlib.Path:
        return self.workdir / "source.S"

    @property
    def executable_path(self) -> pathlib.Path:
        return self.workdir / "a.out"

    async def compile(self, source_code) -> CompilationResult:
        with open(self.source_path, "w") as f:
            f.write(source_code)

        command = [
            config.archs[self.arch].gcc,
            "-no-pie",
            "-nodefaultlibs",
            "-nostartfiles",
            "-static",
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

    async def start_debugger(
        self,
        cpu_usage_limit: Optional[float] = None,
        cpu_time_limit: Optional[int] = None,
        memory_limit: Optional[int] = None,
        real_time_limit: Optional[int] = None
    ) -> None:
        active_debug_sessions.add(self)

        cpu_usage_limit = cpu_usage_limit or config.default_cpu_usage_limit
        cpu_time_limit = cpu_time_limit or config.default_cpu_time_limit
        memory_limit = memory_limit or config.default_memory_limit
        self.real_time_limit = real_time_limit or config.default_real_time_limit

        await self.debugger.start(config.archs[self.arch].gdb)
        await self.debugger.gdb_command(f"-gdb-set mi-async on")
        await self.debugger.gdb_command(f"-file-exec-and-symbols {self.executable_path}")

        gdbstub_docker_params = {
            "Hostname": self.session_id,
            "Cmd": ["sleep", "infinity"],
            "Image": config.executor_docker_image,
            "HostConfig": {
                "CpuQuota": round(cpu_usage_limit * 100000),
                "Memory": memory_limit,
                "Ulimits": [{
                    "Name": "cpu",
                    "Soft": cpu_time_limit,
                    "Hard": cpu_time_limit
                }],
                "NetworkMode": config.docker_network,
                "Binds": [
                    f"{config.runner_data_volume}:{config.runner_data_path}"
                ]
            }
        }

        self.gdbstub_container_id = await docker.create_and_start_container(gdbstub_docker_params)
        await self.start_gdbstub()

    async def start_gdbstub(self) -> None:
        await docker.start_command_in_container(self.gdbstub_container_id, ["killall", "-9", config.archs[self.arch].qemu])

        try:
            await self.debugger.gdb_command("-target-disconnect")
        except DebuggerError:
            pass

        gdbstub_command = []

        if self.real_time_limit:
            gdbstub_command += ["timeout", "-s", "KILL", f"{self.real_time_limit}s"]

        gdbstub_command += [config.archs[self.arch].qemu, "-g", "1234", str(self.executable_path)]

        await docker.start_command_in_container(self.gdbstub_container_id, gdbstub_command)
        await self.debugger.gdb_command(f"-target-select remote {self.session_id}:1234")

    async def close_impl(self) -> None:
        if self.debugger is not None:
            await asyncio.shield(self.debugger.terminate())
        if self.gdbstub_container_id:
            await asyncio.shield(docker.stop_and_delete_container(self.gdbstub_container_id))
        shutil.rmtree(self.workdir)
        active_debug_sessions.discard(self)

    def close(self) -> None:
        if self.closed:
            return
        self.closed = True
        asyncio.create_task(self.close_impl())

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

    async def evaluate_expression(self, expr: str) -> str:
        escaped = expr.replace('"', '\\"')
        gdb_response = await self.debugger.gdb_command(f'-data-evaluate-expression "{escaped}"')
        return gdb_response["value"]

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

    async def restart(self) -> None:
        await self.start_gdbstub()
        await self.continue_until("_start")

    async def read_file_from_remote(self, path: pathlib.Path | str) -> bytes:
        host_path = self.workdir / str(uuid4())
        await self.debugger.gdb_command(f"-target-file-get {path} {host_path}")
        try:
            with open(host_path, "rb") as f:
                contents = f.read()
        except (IOError, OSError):
            raise DebuggerError(f"can't read file {path}")
        host_path.unlink(missing_ok=True)
        return contents

    async def get_total_cpu_time_used(self) -> float:
        data = await self.read_file_from_remote("/sys/fs/cgroup/cpuacct/cpuacct.usage")
        try:
            return int(data) / 10**9
        except ValueError:
            raise DebuggerError(f"invalid file format")

    async def get_memory_used(self) -> int:
        data = await self.read_file_from_remote("/sys/fs/cgroup/memory/memory.usage_in_bytes")
        try:
            return int(data)
        except ValueError:
            raise DebuggerError(f"invalid file format")

    async def get_max_memory_used(self) -> int:
        data = await self.read_file_from_remote("/sys/fs/cgroup/memory/memory.max_usage_in_bytes")
        try:
            return int(data)
        except ValueError:
            raise DebuggerError(f"invalid file format")
