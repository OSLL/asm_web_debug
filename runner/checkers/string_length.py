import ast
from runner.checkerlib import Checker, InvalidSampleTestFormatError, WrongAnswerError


class StringLengthChecker(Checker):
    source_prefix = """
.global _start

.lcomm scratch, 1024

.text

_start:
nop
"""

    source_suffix = """
nop

_end_of_program:
    ret
"""

    sample_test = '"hello"'

    async def check(self) -> None:
        for s in ["hello", "", "abc"]:
            await self.program.restart()

            await self.program.write_memory_region(f"(char*)&scratch", s.encode() + b"\x00")
            await self.program.set_register_value("rdi", f"&scratch")

            await self.program.continue_until("_end_of_program")
            result = await self.program.get_register_value("rax", "d")
            if result != str(len(s)):
                raise WrongAnswerError(f"wrong length of string {s!r}, expected {len(s)}, got {result}")

    async def prepare_sample_test(self) -> None:
        try:
            s = ast.literal_eval(self.sample_test)
            assert type(s) is str
        except Exception as err:
            raise InvalidSampleTestFormatError(f"Invalid sample test: {err}")

        await self.program.write_memory_region(f"(char*)&scratch", s.encode() + b"\x00")
        await self.program.set_register_value("rdi", f"&scratch")
