import os
import subprocess

import app.core.debug.gdb_wrapper

from flask import current_app
from enum import Enum, auto


class QemuUserProcessError(Exception):
    pass

class QemuUserProcess:

    class QemuUserProcessState:
        PROCESSING = '0'
        NOTRUN = '1'
        FINISHED = '2'
        KILLED = '3'


    arch_run_cmd   = {"x86_64" : ["../environment/qemu-x86_64"]}
                    # "ARM" : ["../environment/qemu-arm"]
                    # "AVR" : ["../environment/qemu-system-avr -cpu ... "]


    def __init__(cls, path, arch, debug):

        if not os.path.isfile(path):
            raise QemuUserProcessError('File not found')

        if not arch in current_app.config["ARCHS"]:
	        raise QemuUserProcessError('unknown arch')

        cls.path = path
        cls.arch = arch
        cls.debug = debug

        cls.process_pid = 0

        cls.dbg_port = 0
        cls.state = QemuUserProcess.QemuUserProcessState.NOTRUN


    def get_state(self):
        return self.state


    def run(cls, debug_port = 0):
        run_args = []

        cls.dbg_port = debug_port # random port

        if cls.arch in cls.arch_run_cmd:
            run_args = cls.arch_run_cmd[cls.arch]
        else:
            return { "success_run": False, "run_logs": f"Arch {cls.arch} not supported!" }

        if cls.debug:
            run_args.append('-g')
            run_args.append(str(cls.dbg_port))
        
        # path to binnary file for run
        run_args.append(cls.path) 
        print(cls.path)

        if cls.state == QemuUserProcess.QemuUserProcessState.PROCESSING:
            return { "success_run": False, "run_logs": f"Process already running" }

        cls.state = QemuUserProcess.QemuUserProcessState.PROCESSING
        
        # TODO timeout = ....
        #
        run_result = subprocess.run(run_args, capture_output = True)
        cls.state = QemuUserProcess.QemuUserProcessState.FINISHED
        
        if run_result.returncode == 0:
            status = 'success'
        else:
            status = run_result.returncode

        cls.dbg_port = 0

        return { "success_run": True, "run_logs": f"STATUS: {status};\nstdout: {run_result.stdout};\nstderr: {run_result.stderr};\n" }


    def debug(cls):
        pass


    def kill(cls):
        cls.state = QemuUserProcess.QemuUserProcessState.KILLED
        #os.kill(self.process_pid)
        #os.kill(self.gdb_pid)


    def get_pid(cls):
        return cls.process_pid


    def get_debug_port(cls):
        return cls.dbg_port


