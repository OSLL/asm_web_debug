import signal
import subprocess
import uuid
from flask import current_app


class UserProcess:
    def __init__(self, exe_path, arch="x86_64"):
        self.exe_path = exe_path
        self.arch = arch
        self.uuid = uuid.uuid4()
        self.gdb = None
        self.program = None

    def start_with_debugger(self):
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

        self.program = subprocess.Popen(
            qemu_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

        self.gdb = subprocess.Popen(
            gdb_cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE
        )

    def gdb_command(self, command):
        if self.gdb is None:
            raise RuntimeError(f"Failed to execute GDB command {command!r}: no debugger attached")

    def terminate(self):
        if self.gdb is not None:
            self.gdb_command("-exec-abort")
            self.gdb_command("-gdb-exit")
        elif self.program is not None:
            self.program.send_signal(signal.SIGKILL)
        self.gdb = None
        self.program = None
