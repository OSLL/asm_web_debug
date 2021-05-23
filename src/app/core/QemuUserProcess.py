import os
import subprocess
from flask import current_app
from enum import Enum, auto



class QemuUserProcessError(Exception):
    pass


class QemuUserProcessMode(Enum):
    RUN = '1'
    DEBUG = '2'
    SINGLESTEP = '3'


class QemuUserProcess:

    arch_run_cmd   = {"x86_64" : "../environment/qemu-x86_64"}
                    # "ARM" : "../environment/qemu-arm"
                    # "AVR" : "../environment/qemu-system-avr -cpu ... "

    def __init__(self, path, arch, mode = QemuUserProcessMode.RUN, port = 0):

        if not os.path.isfile(path):
            raise QemuUserProcessError('File not found')

        if not arch in current_app.config["ARCHS"]:
	        raise QemuUserProcessError('unknown arch')

        self.path = path
        self.arch = arch
        self.mode = mode

        self.pid = 0
        self.dbg_pid = 0
        self.dbg_port = port
        self.status = 0


    def get_status(self, uid):
        pass


    def run(self, uid):
        
        qemu_emul = ["../environment/qemu-x86_64"]
        qemu_emul.append('-g')
        qemu_emul.append(str(self.dbg_port))
        qemu_emul.append(self.path)
        run_result = subprocess.run(qemu_emul, capture_output = True)


    def finish(self, uid):
        pass


    def get_pids(self, uid):
        pass


    def get_debug_port(self, uid):
        pass


