from pygdbmi.constants import GdbTimeoutError, DEFAULT_GDB_TIMEOUT_SEC
from pygdbmi.gdbcontroller import GdbController


class gdb_wrapper(object):
    class no_response(object):
        def __call__(self, function):
            def wrapper(*args, **kwargs):
                try:
                    return function(*args, **kwargs)
                except GdbTimeoutError:
                    return "Did not get response from gdb after {} seconds".format(
                        kwargs['timeout_sec'] if 'timeout_sec' in kwargs else DEFAULT_GDB_TIMEOUT_SEC)
            return wrapper

    def __init__(self, port=None, file=None):
        self.breakpoints = {}
        self.pid = self.gdb_ctrl.gdb_process.pid
        if port is not None:
            self.connect_to_port(port)
        if file is not None:
            self.gdb_ctrl.write("file " + file)

    @staticmethod
    def __parse_log(log, type):
        for el in log:
            if el['type'] == type:
                return el

    @no_response()
    def get_registers(self, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        # надо проверить что процесс запущен
        result = []
        log = self.gdb_ctrl.write("-data-list-register-names", timeout_sec)
        indexes_of_registers = [index for index, elem in enumerate(log[0]['payload']['register-names']) if
                                elem in self.__registers]
        result.append([elem for elem in log[0]['payload']['register-names'] if elem in self.__registers])
        index_of_flags = 0
        if self.__flags_name in self.__registers:
            index_of_flags = result[0].index(self.__flags_name)

        log = self.gdb_ctrl.write("-data-list-register-values r {}".format(indexes_of_registers), timeout_sec)
        if self.__parse_log(log, 'result')['message'] == 'error':
            return []
        # Это значит что процесс не запущен
        result.append([reg_value['value'] for reg_value in log[0]['payload']['register-values']])
        if self.__flags_name in self.__registers:
            result[1][index_of_flags] = self.get_flags()
        return result

    @no_response()
    def connect_to_port(self, port, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        log = self.gdb_ctrl.write("target extended-remote localhost:" + str(port), timeout_sec)
        return log

    @no_response()
    def step_over(self, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        log = self.gdb_ctrl.write("-exec-next", timeout_sec)
        return log

    @no_response()
    def step_in(self, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        log = self.gdb_ctrl.write("-exec-step", timeout_sec)
        return log

    # Если у нас только внешняя функция, то он ничего не сделает
    @no_response()
    def step_out(self, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        log = self.gdb_ctrl.write("-exec-finish", timeout_sec)
        return log

    @no_response()
    def get_stack(self, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        log = self.gdb_ctrl.write("-stack-list-frames", timeout_sec)
        if log[0]['message'] == 'error':
            return {}
        return log[0]['payload']

    @no_response()
    def get_registers(self, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        # надо проверить что процесс запущен
        result = []
        log = self.gdb_ctrl.write("-data-list-register-names", timeout_sec)
        indexes_of_registers = [index for index, elem in enumerate(log[0]['payload']['register-names']) if
                                elem in self.__registers]
        result.append([elem for elem in log[0]['payload']['register-names'] if elem in self.__registers])
        index_of_eflags = 0
        if self.__eflag_name in self.__registers:
            index_of_eflags = result[0].index(self.__eflag_name)

        log = self.gdb_ctrl.write("-data-list-register-values r {}".format(indexes_of_registers), timeout_sec)
        if self.__parse_log(log, 'result')['message'] == 'error':
            return []
        # Это значит что процесс не запущен

        result.append([reg_value['value'] for reg_value in log[0]['payload']['register-values']])
        if self.__eflag_name in self.__registers:
            log = self.gdb_ctrl.write("print ${}".format(self.__eflag_name), timeout_sec)
            _, _, values = self.__parse_log(log, 'console')['payload'].partition(' = ')
            if self.arch == 'avr':
                all_flags = ['C', 'Z', 'N', 'V', 'S', 'H', 'T', 'I']
                result[1][index_of_eflags] = [all_flags[i] for i in range(8) if int(values.rstrip()) & 1 << i]
            elif self.arch == 'arm':
                result[1][index_of_eflags] = int(values.rstrip())
            else:
                result[1][index_of_eflags] = values.rstrip().strip('][').split()
        return result

    @no_response()
    def write(self, command, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        if command.strip() == "q":
            self.gdb_ctrl.exit()
            return ""
        log = self.gdb_ctrl.write(command, timeout_sec)
        return log

    @no_response()
    def quit(self):
        self.gdb_ctrl.exit()


class gdb_wrapper_x86_64(gdb_wrapper):
    def __init__(self, port=None, file=None):
        self.gdb_ctrl = GdbController(["gdb-multiarch", "-q", "--interpreter=mi"])
        self.gdb_ctrl.write("set architecture auto")
        self.__registers = {'r{}'.format(i) for i in range(8, 16)}
        self.__registers.update({'rax', 'rdi', 'rsi', 'rdx', 'rcx', 'rbx', 'rsp', 'rbp', 'rip', 'eflags'})
        # self.__registers.update({'eax', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'esp', 'ebp', 'eip'})
        self.__flags_name = 'eflags'
        super().__init__(port, file)

    @gdb_wrapper.no_response()
    def get_flags(self, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        log = self.gdb_ctrl.write("print ${}".format(self.__flags_name), timeout_sec)
        _, _, values = self.__parse_log(log, 'console')['payload'].partition(' = ')
        return values.rstrip().strip('][').split()


class gdb_wrapper_arm(gdb_wrapper):
    def __init__(self, port=None, file=None):
        self.gdb_ctrl = GdbController(["gdb-multiarch", "-q", "--interpreter=mi"])

        self.__registers = {'r{}'.format(i) for i in range(13)}
        self.__registers.update({'sp', 'lr', 'pc', 'cpsr'})
        self.__flags_name = 'cpsr'
        super().__init__(port, file)

    @gdb_wrapper.no_response()
    def get_flags(self, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        log = self.gdb_ctrl.write("print ${}".format(self.__flags_name), timeout_sec)
        _, _, values = self.__parse_log(log, 'console')['payload'].partition(' = ')
        return int(values.rstrip())


class gdb_wrapper_avr(gdb_wrapper):
    def __init__(self, port=None, file=None):
        self.gdb_ctrl = GdbController(["avr-gdb", "-q", "--interpreter=mi"])
        self.__registers = {'r{}'.format(i) for i in range(32)}
        self.__registers.update({'SP', 'PC', 'SREG'})
        self.__flags_name = 'SREG'
        super().__init__(port, file)

    @gdb_wrapper.no_response()
    def get_flags(self, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        all_flags = ['C', 'Z', 'N', 'V', 'S', 'H', 'T', 'I']
        log = self.gdb_ctrl.write("print ${}".format(self.__flags_name), timeout_sec)
        _, _, values = self.__parse_log(log, 'console')['payload'].partition(' = ')
        return [all_flags[i] for i in range(8) if int(values.rstrip()) & 1 << i]


# basic test to be improved and should be output in a separate file
if __name__ == '__main__':
    from demo_debug.py_demo.as_run import as_runner
    from demo_debug.py_demo.ld_run import ld_runner
    from demo_debug.py_demo.qemu_run import qemu_runner

    prog_dir = "demo_debug/demos"
    arg_arch = "avr"
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

    gdbrun = gdb_wrapper_avr(qmrun.dbg_port, qmrun.cur_exec)
    print('go')
    while True:
        gcmd = input()
        if gcmd == 'info reg':
            print(gdbrun.get_registers())
        elif gcmd == 'info stack':
            print(gdbrun.get_stack())
        elif gcmd == 'n':
            print(gdbrun.step_over())
        else:
            resp = gdbrun.write(gcmd, timeout_sec=2)
            print(resp, end='')
        if gcmd == 'q':
            break
