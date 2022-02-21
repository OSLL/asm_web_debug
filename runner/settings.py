from dataclasses import dataclass, field
import pathlib
import sys
from typing import Dict, List


@dataclass
class Arch:
    gcc: str
    gdb: str
    display_registers: List[str]


@dataclass
class Config:
    host: str = "0.0.0.0"
    port: int = 80
    archs: Dict[str, Arch] = field(default_factory=lambda: {
        "x86_64": Arch(gcc="gcc", gdb="gdb", display_registers=["rax", "rbx", "rcx", "rdx", "rsi", "rdi", "rbp", "rsp", "r8", "r9", "r10", "r11", "r12", "r13", "r14", "r15", "rip", "eflags"])
    })

root: pathlib.Path = pathlib.Path(__file__).parent.parent
config: Config = Config()
