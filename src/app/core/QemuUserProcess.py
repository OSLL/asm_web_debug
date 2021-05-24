import os
import subprocess

import app.core.debug.gdb_wrapper

from flask import current_app
from enum import Enum, auto


class QemuUserProcessError(Exception):
    pass


class QemuUserProcessMode(Enum):
    RUN = '1'
    DEBUG = '2'
    SINGLESTEP = '3'


class QemuUserProcess:

    class QemuUserProcessState:
        PROCESSING = '0'
        NOTRUN = '1'
        FINISHED = '2'
        KILLED = '3'


    arch_run_cmd   = {"x86_64" : ["../environment/qemu-x86_64"]}
                    # "ARM" : ["../environment/qemu-arm"]
                    # "AVR" : ["../environment/qemu-system-avr -cpu ... "]

    def __init__(self, path, arch):

        if not os.path.isfile(path):
            raise QemuUserProcessError('File not found')

        if not arch in current_app.config["ARCHS"]:
	        raise QemuUserProcessError('unknown arch')

        self.path = path
        self.arch = arch
        self.mode = QemuUserProcessMode.RUN

        self.process_pid = 0
        self.dbg_pid = 0

        self.dbg_port = 0
        self.state = QemuUserProcess.QemuUserProcessState.NOTRUN


    def get_state(self):
        return self.state


    def run(self, mode = QemuUserProcessMode.RUN):
        run_args = []

        self.mode = mode
        self.dbg_port = 1234 # random port

        if self.arch in self.arch_run_cmd:
            run_args = self.arch_run_cmd[self.arch]
        else:
            return { "success_run": False, "run_logs": f"Arch {self.arch} not supported!" }

        if self.mode == QemuUserProcessMode.DEBUG:
            run_args.append('-g')
            run_args.append(str(self.dbg_port))
        
        # path to binnary file for run
        run_args.append(self.path) 
        print(self.path)

        if self.state == QemuUserProcess.QemuUserProcessState.PROCESSING:
            return { "success_run": False, "run_logs": f"Process already running" }

        self.state = QemuUserProcess.QemuUserProcessState.PROCESSING
        
        run_result = subprocess.run(run_args, capture_output = True)
        self.state = QemuUserProcess.QemuUserProcessState.FINISHED
        
        if run_result.returncode == 0:
            status = 'success'
        else:
            status = run_result.returncode

        return { "success_run": True, "run_logs": f"STATUS: {status};\nstdout: {run_result.stdout};\nstderr: {run_result.stderr};\n" }


    def debug(self):
        pass


    def kill(self):
        self.state = QemuUserProcess.QemuUserProcessState.KILLED
        #os.kill(self.process_pid)
        #os.kill(self.gdb_pid)


    def get_pids(self):
        return [self.process_pid, self.dbg_pid]


    def get_debug_port(self):
        return self.dbg_port


