import subprocess
import os
from flask import current_app


class CompileError(Exception):
    pass


class ASManager:
    # Static methods:

    # Description:
    # Compiles a file using assembler program with specified architecture.
    # Arguments:
    # 	filename - name of source file to be compiled (.s)
    # 	arch - architecture name string
    # 	dependence - depend files dir path
    # Return values:
    # 	1) [bool] if compiling was successful
    # 	2) [str] as logs
    @classmethod
    def compile(cls, filename, arch):
        # Remembering information about compiled file
        arch = arch
        filename = filename
        binary_filename = filename + ".bin"
        build_flags = []
        exec_path = None

        if not arch in current_app.config["ARCHS"]:
            raise CompileError(f"Compile error: unknown arch: {arch}")

        if not os.path.isfile(filename):
            raise FileNotFoundError(
                "Compile error: file '{0}' not found".format(filename)
            )

        arch_cfg = current_app.config["ARCHS"][arch]

        # Forming arguments to as process
        args = [
            arch_cfg.get("toolchain_prefix", "") + "gcc",
            "-no-pie",
            "-nodefaultlibs",
            "-nostartfiles",
            "-g",
        ]

        if arch_cfg.get("seccomp", False):
            # use seccomp
            args.extend(
                [
                    "-Wl,--entry=_start_seccomp",
                    os.path.join(
                        current_app.config["ENVIRONMENT_FOLDER"],
                        "seccomp",
                        arch,
                        "entry.S",
                    ),
                ]
            )
        args.extend([filename, "-o", binary_filename])

        # Returning response from as
        as_resp = subprocess.run(args, capture_output=True)

        return not as_resp.returncode, as_resp.stderr, as_resp.stdout
