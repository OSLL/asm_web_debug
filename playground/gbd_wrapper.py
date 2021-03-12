from pygdbmi.gdbcontroller import GdbController
from demo_debug.py_demo.gdb_logger import get_payload_str


class gdb_wrapper:
    def __init__(self, arch, port=None, file=None):
        self.arch = arch
        self.gdb_ctrl = GdbController(["demo_debug/gdb_binaries/gdb_" + arch, "-q", "--interpreter=mi"])
        self.pid = self.gdb_ctrl.gdb_process.pid
        if port is not None:
            self.connect_to_port(port)
        if file is not None:
            self.write("file " + file)

    @staticmethod
    def __parse_log(log):
        return get_payload_str(log, [("stdout", "console"), ("stdout", "log")])

    def connect_to_port(self, port):
        log = self.gdb_ctrl.write("target extended-remote localhost:" + str(port))
        return log


    def step_over(self, number=1):
        log = self.gdb_ctrl.write("next " + str(number))
        return self.__parse_log(log)

    def step_in(self, number=1):
        log = self.gdb_ctrl.write("step " + str(number))
        return self.__parse_log(log)

    def step_out(self):
        log = self.gdb_ctrl.write("finish")
        return self.__parse_log(log)


    def get_stack(self):
        log = self.gdb_ctrl.write("info stack")
        return self.__parse_log(log)

    # probably this method should return a register-value dictionary

    def get_registers(self):
        log = self.gdb_ctrl.write("info reg")
        return self.__parse_log(log)


    def write(self, command):
        if command.strip() == "q":
            self.quit()
            return ""
        log = self.gdb_ctrl.write(command)
        return self.__parse_log(log)

    def quit(self):
        self.gdb_ctrl.exit()

# basic test to be improved and should be output in a separate file

if __name__ == '__main__':
    from playground.demo_debug.py_demo.as_run import as_runner
    from demo_debug.py_demo.ld_run import ld_runner
    from demo_debug.py_demo.qemu_run import qemu_runner

    prog_dir = "demo_debug/demos"
    arg_arch = "x86_64"
    arg_exec = "demo_helloworld"

    s_path = "{0}/{1}.{2}.s".format(prog_dir, arg_exec, arg_arch)
    o_path = "{0}/{1}.{2}.o".format(prog_dir, arg_exec, arg_arch)
    out_path = "{0}/{1}.{2}.out".format(prog_dir, arg_exec, arg_arch)

    asrun = as_runner(arg_arch)
    resp = asrun.run(s_path, o_path)
    print(str(resp.stdout)[2:-1])
    print(str(resp.stderr)[2:-1])
    if resp.returncode != 0:
        exit(resp.returncode)
    ldrun = ld_runner(arg_arch)
    resp = ldrun.run(o_path, out_path)
    print(str(resp.stdout)[2:-1])
    print(str(resp.stderr)[2:-1])
    if resp.returncode != 0:
        exit(resp.returncode)

    qmrun = qemu_runner(arg_arch)
    qmrun.run(out_path)

    gdbrun = gdb_wrapper(arg_arch, qmrun.dbg_port, qmrun.cur_exec)
    while True:
        gcmd = input()
        if gcmd == 'info reg':
            print(gdbrun.get_registers())
        elif gcmd == 'info stack':
            print(gdbrun.get_stack())
        elif gcmd == 'n':
            print(gdbrun.next())
        else:
            resp = gdbrun.write(gcmd)
            print(resp, end='')
        if gcmd == 'q':
            break
