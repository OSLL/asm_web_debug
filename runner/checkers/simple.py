from dataclasses import dataclass
from typing import Dict

from runner.checkerlib import Checker


class SimpleChecker(Checker):
    @dataclass
    class Config:
        initial_register_values: Dict[str, str]
        expected_register_values: Dict[str, str]

    async def run(self, config: "Config") -> None:
        program = await self.start(f"""
.global _start
.text

_start:
    {self.source_code}

nop

_end_of_program:
    ret
""")

        for register, value in config.initial_register_values.items():
            await program.set_register_value(register, value)

        await program.continue_until("_end_of_program")

        for register, expected_value in config.expected_register_values.items():
            value = await program.get_register_value(register)
            assert value == expected_value
