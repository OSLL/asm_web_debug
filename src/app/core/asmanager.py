import subprocess
import os
from flask import current_app


class CompileError(Exception):
    pass


class ASManager:
    # Constants:
    arch_exec_path = {"x86_64": "gcc",
                      "ARM": "arm-linux-gnueabi-as",
                      "AVR": "avr-as"}

    arch_build_flags = {"x86_64": ["-no-pie", "-nodefaultlibs", "-nostartfiles", "-g"],
                        "AVR": ["-g", "-mmcu=avr6"],
                        "ARM": ["-march=armv7-a", "-mcpu=cortex-a5"]}

    arch_link_flags = {"AVR": ["avr-ld", "-m avr1"],
                       "x86_64": ["x86_64-linux-gnu-ld", "-melf_i386"],
                       "ARM": ["arm-none-eabi-ld"]}

    # Static methods:

    # Description:
    # Compiles a file using assembler program with specified architecture.
    # Arguments:
    #	filename - name of source file to be compiled (.s)
    #	arch - architecture name string
    #	dependence - depend files dir path
    # Return values:
    #	1) [bool] if compiling was successful
    #	2) [str] as logs
    @classmethod
    def compile(cls, filename, arch):
        # Remembering information about compiled file
        arch = arch
        filename = filename
        binary_filename = filename + ".bin"
        build_flags = []
        exec_path = None

        if not arch in current_app.config["ARCHS"] or not arch in cls.arch_exec_path:
            raise CompileError(f'Compile error: unknown arch: {arch}')

        if not os.path.isfile(filename):
            raise FileNotFoundError('Compile error: file \'{0}\' not found'.format(filename))

        # Setting up run flags
        if arch in cls.arch_build_flags:
            build_flags.extend(cls.arch_build_flags[arch])

        # Setting up executable path
        if arch in cls.arch_exec_path:
            exec_path = cls.arch_exec_path[arch]
        else:
            raise CompileError('unknown arch')

        # Forming arguments to as process
        args = [exec_path]
        args.extend(build_flags)
        if arch == "x86_64":
            # use seccomp
            args.extend(["-Wl,--entry=_start_seccomp",
                         os.path.join(current_app.config["ENVIRONMENT_FOLDER"], "seccomp", "x86_64", "entry.S")])
        args.extend([filename, "-o", binary_filename])

        # Returning response from as
        as_resp = subprocess.run(args, capture_output=True)

        return not as_resp.returncode, as_resp.stderr, as_resp.stdout
