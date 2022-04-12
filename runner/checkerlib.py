import abc
import pathlib
from typing import Dict, Optional, Type
from runner import gdbmi
from runner.settings import config
from runner.debugger import DebuggerError
from runner.runner import DebugSession

class CheckerException(Exception): pass

class DoesNotCompileError(CheckerException): pass
class WrongAnswerError(CheckerException): pass
class SignalledError(CheckerException): pass
class InternalCheckerError(CheckerException): pass
class InvalidSampleTestFormatError(CheckerException): pass


class BaseChecker(abc.ABC):
    arch: str
    source_code: str
    _cleanup: list

    @abc.abstractmethod
    async def run(self) -> None: pass

    _all_checkers: "Dict[str, Type[Checker]]" = {}

    def __init_subclass__(cls, **kwargs) -> None:
        super().__init_subclass__(**kwargs)
        if cls.__name__ != "Checker":
            cls._all_checkers[cls.__name__] = cls

    def __init__(self, arch: str, source_code: str) -> None:
        self.arch = arch
        self.source_code = source_code
        self._cleanup = []

    async def start(self, source_code: Optional[str], params: Optional[dict] = None) -> DebugSession:
        if params is None:
            params = {}
        debug_session = DebugSession(self.arch)
        self._cleanup.append(debug_session.close)

        if not source_code:
            source_code = self.source_code

        compilation_result = await debug_session.compile(source_code)
        if not compilation_result.successful:
            raise DoesNotCompileError(str(compilation_result.stderr))

        await debug_session.start_debugger(**params)

        def on_event(event: gdbmi.AnyNotification) -> None:
            if type(event) is gdbmi.ExecAsync and event.status == "stopped":
                reason = event.values["reason"]
                if reason in ("signal-received", "exited-signalled") and event.values["signal-name"] != "SIGINT":
                    raise SignalledError(event.values["signal-name"])

        debug_session.event_subscribers.append(on_event)
        await debug_session.restart()

        return debug_session

    def close(self) -> None:
        for fn in self._cleanup:
            fn()

    @classmethod
    async def run_checker_by_name(cls, checker_name: str, config: dict, arch: str, source_code: str) -> None:
        if checker_name not in cls._all_checkers:
            raise ValueError("Invalid checker name")

        checker_class = cls._all_checkers[checker_name]
        checker = checker_class(arch=arch, source_code=source_code)

        for key, value in config.items():
            setattr(checker, key, value)

        try:
            await checker.run()
        except DebuggerError as err:
            raise InternalCheckerError(err)
        finally:
            checker.close()

    def get_source_for_interactive_debugger(self) -> str:
        return self.source_code


class Checker(BaseChecker):
    source_prefix: str = ""
    source_suffix: str = ""
    sample_test: Optional[str] = None

    cpu_usage_limit: Optional[float] = None # in cores
    cpu_time_limit: Optional[int] = None    # in seconds
    memory_limit: Optional[int] = None      # in bytes
    real_time_limit: Optional[int] = None   # in seconds

    program: DebugSession

    async def check_before_run(self) -> None: pass
    async def check(self) -> None: pass
    async def prepare_sample_test(self) -> None: pass

    def get_source_for_interactive_debugger(self) -> str:
        return f"""{self.source_prefix}
#line 1
{self.source_code}
{self.source_suffix}
"""

    async def run(self) -> None:
        await self.check_before_run()
        self.program = await self.start(self.get_source_for_interactive_debugger(), params={
            "cpu_usage_limit": self.cpu_usage_limit,
            "cpu_time_limit": self.cpu_time_limit,
            "memory_limit": self.memory_limit,
            "real_time_limit": self.real_time_limit
        })
        await self.check()
