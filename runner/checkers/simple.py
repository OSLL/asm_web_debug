from typing import Dict

from runner.checkerlib import Checker, WrongAnswerError


class SimpleChecker(Checker):
    initial_register_values: Dict[str, str]
    expected_register_values: Dict[str, str]

    source_prefix = """
.global _start
.text

_start:
"""

    source_suffix = """
nop

_end_of_program:
    ret
"""

    async def check(self) -> None:
        for register, value in self.initial_register_values.items():
            await self.program.set_register_value(register, value)

        await self.program.continue_until("_end_of_program")

        for register, expected_value in self.expected_register_values.items():
            value = await self.program.get_register_value(register)
            if value != expected_value:
                raise WrongAnswerError(f"{register} has value {value}, expected {expected_value}")
