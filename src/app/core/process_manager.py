import os
import subprocess
from flask import current_app

class QemuUserProcess:
    def __init__(self, uid, path, arch):
        self.uid = uid
        self.path = path
        self.arch = arch

        self.pid = 0
        self.dbg_pid = 0
        self.dbg_port = 0
        self.status = 0

class ProcessManagerError(Exception):
    pass

class ProcessManager:
    process_list = { }

    def __init__(self):
        pass

    def add_process(self, uid, path, arch):
        if not os.path.isfile(path):
            raise ProcessManagerError('File not found')

        if not arch in current_app.config["ARCHS"]:
	        raise ProcessManagerError('unknown arch')

        process = QemuUserProcess(uid, path, arch)
        self.process_list[uid] = process


    def get_status(self, uid):
        process = self.process_list.get(uid, None)
        if process == None:
            return 0

        return process.status

    def run(self, uid):
        process = self.process_list.get(uid, None)
        if process == None:
            raise ProcessManagerError('process with {0} uid not found'.format(uid))
        
        #only x86
        if process.arch != "x86":
            raise ProcessManagerError('arch TODO')
        subprocess.run(["qemu-system-x86_64", "-kernel", process.path, "-m", "10M", "-no-reboot"])

    def finish(self, uid):
        pass

    def get_pids(self, uid):
        process = self.process_list.get(uid, None)
        if process == None:
            return 0

        return process.pid, process.dbg_pid

    def get_debug_port(self, uid):
        process = self.process_list.get(uid, None)
        if process == None:
            return 0

        return process.dbg_port
