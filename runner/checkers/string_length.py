from runner.checkerlib import Checker, WrongAnswerError


class StringLengthChecker(Checker):
    source_prefix = """
.global _start
.text

_start:
"""

    source_suffix = """
nop

_end_of_program:
    ret


_string_0: .ascii "hello"
_string_1: .ascii ""
_string_2: .ascii "abc"
"""

    async def check(self) -> None:
        for i, s in enumerate(["hello", "", "abc"]):
            await self.program.restart()

            await self.program.write_memory_region(f"(char*)_string_{i}", s.encode() + b"\x00")
            await self.program.set_register_value("rdi", f"_string_{i}")

            await self.program.continue_until("_end_of_program")
            result = await self.program.get_register_value("rax", "d")
            if result != str(len(s)):
                raise WrongAnswerError(f"wrong length of string {s!r}, expected {len(s)}, got {result}")
