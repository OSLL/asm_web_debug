import asyncio
import uuid
from flask import current_app

import app.core.utils.gdbmi as gdbmi


class ProcessManager:
    def __init__(self):
        self.processes = {}


class UserProcess:
    def __init__(self, exe_path, arch="x86_64"):
        self.exe_path = exe_path
        self.arch = arch
        self.uuid = uuid.uuid4()
        self.gdb = None
        self.program = None
        self.requests = asyncio.Queue()
        self.responses = asyncio.Queue()
        self.events = asyncio.Queue()

    async def start_with_debugger(self):
        arch_cfg = current_app.config["ARCHS"][self.arch]
        port = "31415"  # TODO: pick properly

        qemu_cmd = [
            arch_cfg["qemu"],
            "-g",
            port
        ]

        gdb_cmd = [
            arch_cfg.get("toolchain_prefix", "") + "gdb",
            "-q",
            "-nx",
            "--interpreter=mi2"
        ]

        self.program = await asyncio.subprocess.create_subprocess_exec(*qemu_cmd)
        self.gdb = await asyncio.subprocess.create_subprocess_exec(*gdb_cmd)

    async def gdb_interactor(self):
        while self.gdb is not None:
            line = await self.gdb.stdout.readline()
            if not line:
                break
            gdb_response = gdbmi.parse_gdb_response(line.decode())
            print(gdb_response)
            if gdb_response is gdbmi.Result:
                await self.responses.put(gdb_response)
            else:
                await self.events.put(gdb_response)

    async def gdb_command(self, command):
        if self.gdb is None:
            raise RuntimeError(f"Failed to execute GDB command {command!r}: no debugger attached")

        await self.requests.put(command)
        return await self.responses.get()

    async def terminate(self):
        if self.gdb is not None:
            await self.gdb_command("-gdb-exit")
            await self.gdb.wait()
        elif self.program is not None:
            await self.program.kill()

        self.gdb = None
        self.program = None
