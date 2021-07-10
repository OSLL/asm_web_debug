import os
import subprocess
import asyncio
from flask import current_app

class ProcessManagerError(Exception):
    pass



class QemuUserProcess:
    process_list = { }

    def __init__(self, path, arch):

        if not os.path.isfile(path):
                raise ProcessManagerError('File not found')

        if not arch in current_app.config["ARCHS"]:
	        raise ProcessManagerError('unknown arch')

        self.path = path
        self.arch = arch

        self.pid = -1
        self.dbg_pid = 0
        self.dbg_port = 0
        self.status = 0


    def add_process(self, uid, path, arch):
        if not os.path.isfile(path):
            raise ProcessManagerError('File not found')

        if not arch in current_app.config["ARCHS"]:
	        raise ProcessManagerError('unknown arch')

        process = QemuUserProcess(path, arch)
        QemuUserProcess.process_list[uid] = process


    def get_status(self, uid):
        process = QemuUserProcess.process_list.get(uid, None)
        if process == None:
            return 0

        return process.status

    async def __async_subp_run(self, sh_com):
        proc = await asyncio.create_subprocess_shell(sh_com, None,
                                        asyncio.subprocess.DEVNULL, asyncio.subprocess.DEVNULL)
        await proc.wait()
        return proc

    def run(self, uid):
        process = QemuUserProcess.process_list.get(uid, None)
        if process == None:
            raise ProcessManagerError('process with {0} uid not found'.format(uid))
        process.pid = 10
        if process.arch == "x86_64":
                loop = asyncio.new_event_loop()
                prhn = loop.run_until_complete(self.__async_subp_run(
                                             "qemu-x86_64 {0}".format(process.path)))
                if prhn:
                    process.pid = prhn.pid
                    process.status = prhn.returncode
        elif process.arch == "AVR":
                loop = asyncio.new_event_loop()
                prhn = loop.run_until_complete(self.__async_subp_run(
                                             "qemu-system-avr -machine mega -display none -S -gdb tcp::{0} -bios {1}".format(process.dbg_port, process.path)))
                if prhn:
                    process.pid = prhn.pid
                    process.status = prhn.returncode
        else:
	        raise ProcessManagerError('arch TODO:' + process.arch)

    def finish(self, uid):
        pass

    def get_pids(self, uid):
        process = QemuUserProcess.process_list.get(uid, None)
        if process == None:
            return 0

        return process.pid, process.dbg_pid

    def get_debug_port(self, uid):
        process = QemuUserProcess.process_list.get(uid, None)
        if process == None:
            return 0

        return process.dbg_port
