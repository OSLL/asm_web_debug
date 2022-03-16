from dataclasses import dataclass, field
import pathlib
import sys
from typing import Dict, List


@dataclass
class Arch:
    gcc: str
    gdb: str
    gdbserver: str
    display_registers: List[str]


@dataclass
class Config:
    host: str = "0.0.0.0"
    port: int = 80
    archs: Dict[str, Arch] = field(default_factory=lambda: {
        "x86_64": Arch(
            gcc="gcc",
            gdb="gdb",
            gdbserver="gdbserver",
            display_registers=["rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rbp", "rsp", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15", "rip", "eflags"]
        )
    })

    default_cpu_usage_limit: str = "0.1"
    default_memory_limit: str = "32m"
    default_real_time_limit: int = 3600
    default_offline_real_time_limit: int = 10

    executor_docker_image: str = "asm_web_debug_executor"
    runner_data_volume: str = "asm_web_debug_runner_data"
    runner_data_path: str = "/runner_data"

root: pathlib.Path = pathlib.Path(__file__).parent.parent
config: Config = Config()
