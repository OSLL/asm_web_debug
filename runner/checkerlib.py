import abc
from typing import Dict, Optional

from runner.runner import RunningProgram


class DoesNotCompile(Exception): pass


class Checker(abc.ABC):
    class Config: pass

    arch: str
    source_code: str
    cleanup: list

    @abc.abstractmethod
    async def run(self, config: "Config") -> None: pass

    _all_checkers: "Dict[str, Checker]" = {}

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        cls._all_checkers[cls.__name__] = cls

    def __init__(self, arch: str, source_code: str) -> None:
        self.arch = arch
        self.source_code = source_code
        self.cleanup = []

    async def start(self, source_code: Optional[str]) -> RunningProgram:
        running_program = RunningProgram(self.arch)
        self.cleanup.append(running_program)

        if not source_code:
            source_code = self.source_code

        compilation_result = await running_program.compile(source_code)
        if not compilation_result.successful:
            raise DoesNotCompile(str(compilation_result.stderr))

        await running_program.start_debugger()

        breakpoint_id = await running_program.add_breakpoint("_start")
        await running_program.start_program()
        await running_program.wait_until_stopped()
        await running_program.remove_breakpoint(breakpoint_id)

        return running_program

    async def close(self) -> None:
        for obj in self.cleanup:
            await obj.close()

    @classmethod
    async def run_checker(cls, checker_name: str, config: dict, arch: str, source_code: str) -> None:
        if checker_name not in cls._all_checkers:
            raise ValueError("Invalid checker name")

        checker_class = cls._all_checkers[checker_name]
        checker: Checker = checker_class(arch=arch, source_code=source_code)
        try:
            await checker.run(checker_class.Config(**config))
        finally:
            await checker.close()
