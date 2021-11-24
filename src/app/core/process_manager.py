import asyncio
import os.path
import tempfile
import uuid
from flask import current_app

import app.core.utils.gdbmi as gdbmi
from app.core.compile_manager import CompileManager


class ProcessManager:
    processes = {}
    tmpdirs = {}

    @classmethod
    async def cleanup(cls, id):
        if id in cls.processes:
            await cls.processes[id].terminate()
            del cls.processes[id]

        if id in cls.tmpdirs:
            cls.tmpdirs[id].cleanup()
            del cls.tmpdirs[id]

    @classmethod
    async def start_debugging(cls, source_code, arch):
        id = uuid.uuid4()
        cls.tmpdirs[id] = tempfile.TemporaryDirectory(prefix="asm_web_debug_compile")
        tmpdir = cls.tmpdirs[id].name

        src_path = os.path.join(tmpdir, "source.S")
        exe_path = os.path.join(tmpdir, f"binary.{arch}")
        with open(src_path, "w") as f:
            f.write(source_code)
        result = await CompileManager.compile(src_path, exe_path)
        if not result.successful:
            await cls.cleanup(id)
            raise RuntimeError("Compile error")

        cls.processes[id] = UserProcess(id, exe_path, arch)
        await cls.processes[id].start_with_debugger()
        await cls.processes[id].gdb_command(f"-file-exec-and-symbols {exe_path}")
        return cls.processes[id]


class UserProcess:
    def __init__(self, id, exe_path, arch):
        self.id = id
        self.exe_path = exe_path
        self.arch = arch
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

        asyncio.get_event_loop().create_task(self.gdb_interactor())

        await self.gdb_command(f"-target-select remote :{port}")

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

    async def aclose(self):
        await self.terminate()
        await ProcessManager.cleanup(self.id)
