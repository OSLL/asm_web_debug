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
        cls.process_hndl = None
        cls.process_time_start = None # TODO

        cls.dbg_port = 0
        cls.state = QemuUserProcess.QemuUserProcessState.NOTRUN


    def get_state(self):
        return self.state


    def run(cls, debug_port = 0):
        run_args = []

        cls.dbg_port = debug_port

        if cls.arch in cls.arch_run_cmd:
            run_args = cls.arch_run_cmd[cls.arch]
        else:
            return { "success_run": False, "run_logs": f"Arch {cls.arch} not supported!" }

        if cls.debug:
            run_args.append('-g')
            run_args.append(str(cls.dbg_port))
        
        # path to binnary file for run
        run_args.append(cls.path) 

        if cls.state == QemuUserProcess.QemuUserProcessState.PROCESSING:
            return { "success_run": False, "run_logs": f"Process already running" }

        cls.state = QemuUserProcess.QemuUserProcessState.PROCESSING

        cls.process_hndl = subprocess.Popen(run_args, stdout=subprocess.PIPE)  # Execute a child program in a new process.
        ##  run_result = subprocess.run(run_args, capture_output = True)    # Wait for command to complete or timeout, then return the returncode attribute.
        
        cls.process_pid = cls.process_hndl.pid
        
        if not cls.debug:

            data = cls.process_hndl.communicate()
            #Note
            #This will deadlock when using stdout=PIPE or stderr=PIPE and the child process generates enough output to a pipe such that it blocks waiting 
            #for the OS pipe buffer to accept more data. Use Popen.communicate() when using pipes to avoid that. 
            #cls.process_hndl.wait() # TODO .wait(timeout = )
            cls.state = QemuUserProcess.QemuUserProcessState.FINISHED
            
            if cls.process_hndl.returncode == 0:
                status = 'success'
            else:
                status = cls.process_hndl.returncode

            cls.dbg_port = 0

            return { "success_run": True, "run_logs": f"STATUS: {status};\nstdout: {data};\nstderr: {None};\n" }
        

        cls.dbg_port = 0

        return { "success_run": True, "run_logs": f"STATUS: PROCESSING...;\nstdout: {None};\nstderr: {None};\n" }


    def kill(cls):
        cls.state = QemuUserProcess.QemuUserProcessState.KILLED
        cls.process_hndl.terminate()


    def get_pid(cls):
        return cls.process_pid


    def wait_process(cls, timeout = 0):
        cls.process_hndl.wait(timeout)


    def get_debug_port(cls):
        return cls.dbg_port


