import asyncio
import os
from collections import namedtuple

from flask import current_app


CompilationResult = namedtuple("CompilationResult", ["successful", "stdout", "stderr"])


class CompileManager:
    @classmethod
    async def compile(cls, src_path, exe_path, arch):
        if arch not in current_app.config["ARCHS"]:
            raise RuntimeError(f"Compile error: unknown arch: {arch}")

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
        args.extend([src_path, "-o", exe_path])

        process = await asyncio.subprocess.create_subprocess_exec(
            *args,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )

        stdout, stderr = await process.communicate()

        return CompilationResult(
            successful=process.returncode != 0,
            stdout=stdout,
            stderr=stderr
        )
