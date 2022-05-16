from dataclasses import dataclass, field
import pathlib
import os
from typing import Dict, List, Optional


root: pathlib.Path = pathlib.Path(__file__).parent.parent


@dataclass
class Arch:
    gcc: List[str]
    gdb: str
    gdbserver: Optional[str]
    qemu: Optional[List[str]]
    restart: List[str]
    display_registers: List[str]
    entrypoint: str


@dataclass
class Config:
    host: str = "0.0.0.0"
    port: int = 80
    prometheus_port: int = 9090
    archs: Dict[str, Arch] = field(default_factory=lambda: {
        "x86_64": Arch(
            gcc=[
                "gcc",
                "-no-pie",
                "-nodefaultlibs",
                "-nostartfiles",
                "-static",
                "-g",
                "-Wl,--entry=_start_seccomp",
                root / "environment" / "seccomp" / "x86_64" / "entry.S",
            ],
            gdb="gdb",
            gdbserver="gdbserver",
            qemu=None,
            restart=["-exec-run"],
            display_registers=[
                "rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rbp", "rsp", "r8",
                "r9", "r10", "r11", "r12", "r13", "r14", "r15", "eflags"
            ],
            entrypoint="_start"
        ),
        "avr5": Arch(
            gcc=[
                "avr-gcc",
                "-mmcu=atmega328p",
                "-g"
            ],
            gdb="avr-gdb",
            gdbserver=None,
            qemu=["qemu-system-avr", "-machine", "uno", "-nographic"],
            restart=["-gdb-set $pc=0", "-exec-continue"],
            display_registers=[
                "r0", "r1", "r2", "r3", "r4", "r5", "r6", "r7", "r8", "r9", "r10",
                "r11", "r12", "r13", "r14", "r15", "r16", "r17", "r18", "r19", "r20",
                "r21", "r22", "r23", "r24", "r25", "r26", "r27", "r28", "r29", "r30",
                "r31", "SREG", "SP"
            ],
            entrypoint="main"
        )
    })

    default_cpu_usage_limit: float = 0.1
    default_cpu_time_limit: int = 100
    default_memory_limit: int = 32 * 1024 * 1024 # 32 MiB
    default_online_real_time_limit: int = 3600
    default_real_time_limit: int = 10
    default_uninterrupted_real_time_limit: float = 10.0

    executor_docker_image: str = "asm_web_debug_executor"
    runner_data_volume: str = "asm_web_debug_runner_data"
    runner_data_path: str = "/runner_data"
    docker_network: str = "asm_web_debug_default"
    docker_socket: str = "/var/run/docker.sock"
    system_clock_resolution: int = os.sysconf("SC_CLK_TCK")

config: Config = Config()
