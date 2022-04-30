from dataclasses import dataclass
from typing import Any, Dict, List

from runner.checkerlib import Checker, WrongAnswerError


@dataclass
class Test:
    input: Dict[str, Any]
    output: Dict[str, Any]


class RegisterTestsChecker(Checker):
    """
**This checker supports x86_64 and avr5**.

This checker is used to run a program multiple times.
Each time new values are set to specified registers,
and then compared with expected values.

Example config:

    tests:
      - input:
          rax: 2
          rbx: 3
        output:
          rax: 5
      - input:
          rax: 42
          rbx: -42
        output:
          rax: 0
"""

    tests: List[dict]

    source_prefix = {
        "x86_64": """
.global _start
.text

_start:
""",
        "avr5": """
.global main

main:
"""
    }

    source_suffix = """
nop

_end_of_program:
    ret
"""

    async def check(self) -> None:
        for test in self.tests:
            test = Test(**test)
            await self.program.restart()

            for register, value in test.input.items():
                await self.program.set_register_value(register, str(value))

            await self.program.continue_until("_end_of_program")

            for register, expected_value in test.output.items():
                value = await self.program.get_register_value(register)
                if value != str(expected_value):
                    raise WrongAnswerError(f"{register} has value {value}, expected {expected_value}")
