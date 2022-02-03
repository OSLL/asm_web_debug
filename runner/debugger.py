from runner import gdbmi

from typing import Optional, AsyncIterator
import asyncio
import signal


class DebuggerError(Exception):
    pass


class Debugger:
    gdb: Optional[asyncio.subprocess.Process]
    inferior_running: bool
    gdb_results: asyncio.Queue[gdbmi.Result]
    gdb_notifications: asyncio.Queue[gdbmi.AnyNotification | None]
    interactor_task: Optional[asyncio.Task]
    inferior_output_task: Optional[asyncio.Task]

    def __init__(self) -> None:
        self.gdb = None
        self.inferior_running = False
        self.gdb_results = asyncio.Queue()
        self.gdb_notifications = asyncio.Queue()
        self.interactor_task = None
        self.inferior_output_task = None

    async def start(self, path_to_gdb: str) -> None:
        command = [
            path_to_gdb,
            "-q", "-nx",
            "--interpreter=mi2"
        ]

        self.gdb = await asyncio.subprocess.create_subprocess_exec(
            *command,
            stdin=asyncio.subprocess.PIPE,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        self.interactor_task = asyncio.create_task(self._gdb_interactor())
        self.inferior_output_task = asyncio.create_task(self._inferior_output_reader())

    async def _gdb_interactor(self) -> None:
        while self.gdb is not None:
            line = await self.gdb.stdout.readline()
            if not line:
                break

            gdb_response = gdbmi.parse_gdb_response(line.decode())
            if gdb_response is None:
                continue

            if type(gdb_response) is gdbmi.ExecAsync:
                self.inferior_running = gdb_response.status == "running"

            if type(gdb_response) is gdbmi.Result:
                await self.gdb_results.put(gdb_response)
                if gdb_response.status == "exit":
                    break
            else:
                await self.gdb_notifications.put(gdb_response)

        await self.gdb_notifications.put(None)

    async def _inferior_output_reader(self) -> None:
        while self.gdb is not None:
            line = await self.gdb.stderr.readline()
            if not line:
                break
            line = line.decode(errors="replace")
            await self.gdb_notifications.put(gdbmi.TargetOutput(line))

    async def terminate(self) -> None:
        if self.gdb is None:
            return

        self.gdb_interrupt()
        self.gdb.stdin.write("-gdb-exit\n".encode())
        await self.interactor_task
        await self.inferior_output_task
        await self.gdb.wait()
        self.gdb = None
        self.interactor_task = None

    def gdb_interrupt(self):
        self.gdb.send_signal(signal.SIGINT)

    async def gdb_command(self, cmd) -> dict:
        if self.inferior_running:
            need_resume = True
            self.gdb_interrupt()
        else:
            need_resume = False

        self.gdb.stdin.write(f"{cmd}\n".encode())
        result = await self.gdb_results.get()

        if need_resume:
            self.gdb.stdin.write("-exec-continue\n".encode())
            await self.gdb_results.get()

        if result.status == "error":
            raise DebuggerError(result.values)

        return result.values

    async def gdb_notifications_iterator(self) -> AsyncIterator[gdbmi.AnyNotification]:
        while self.gdb is not None:
            notification = await self.gdb_notifications.get()
            if notification is None:
                await self.gdb_notifications.put(None)
                break
            yield notification
