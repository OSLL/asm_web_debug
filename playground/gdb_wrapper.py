from pygdbmi.constants import GdbTimeoutError, DEFAULT_GDB_TIMEOUT_SEC
from pygdbmi.gdbcontroller import GdbController


class gdb_wrapper(object):
    class no_response(object):
        def __call__(self, function):
            def wrapper(*args, **kwargs):
                try:
                    if args[0].need_dump:
                        args[0].gdb_ctrl.get_gdb_response()
                        args[0].need_dump = False
                    return function(*args, **kwargs)
                except GdbTimeoutError:
                    args[0].need_dump = True
                    return "Did not get response from gdb after {} seconds".format(
                        kwargs['timeout_sec'] if 'timeout_sec' in kwargs else DEFAULT_GDB_TIMEOUT_SEC)

            return wrapper

    def __init__(self, port=None, file=None):
        self.breakpoints = {}
        self.pid = self.gdb_ctrl.gdb_process.pid
        self.need_dump = False
        if port is not None:
            self.connect_to_port(port)
        if file is not None:
            self.gdb_ctrl.write("file " + file)

    @staticmethod
    def _parse_log(log, type):
        for el in log:
            if el['type'] == type:
                return el

    @staticmethod
    def _parse_flags(flags_value, all_flags):
        result = {}
        for i in range(len(all_flags)):
            flag_name = all_flags[i]
            if isinstance(flag_name, list):
                if flag_name[0] in result:
                    result[flag_name[0]] += (flags_value >> i & 1) << flag_name[1]
                elif flags_value >> i & 1:
                    result[flag_name[0]] = (flags_value >> i & 1) << flag_name[1]
            else:
                if flags_value >> i & 1:
                    result[flag_name] = 1
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
        if gdb_wrapper._parse_log(log, 'result')['message'] == 'error':
            return {}
        return gdb_wrapper._parse_log(log, 'result')['payload']

    @no_response()
    def get_registers(self, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        # надо проверить что процесс запущен
        result = []
        log = self.gdb_ctrl.write("-data-list-register-names", timeout_sec)
        indexes_of_registers = [index for index, elem in enumerate(log[0]['payload']['register-names']) if
                                elem in self._registers]
        result.append([elem for elem in gdb_wrapper._parse_log(log, 'result')['payload']['register-names'] if
                       elem in self._registers])
        index_of_flags = 0
        if self._flags_name in self._registers:
            index_of_flags = result[0].index(self._flags_name)

        log = self.gdb_ctrl.write("-data-list-register-values r {}".format(indexes_of_registers), timeout_sec)
        if self._parse_log(log, 'result')['message'] == 'error':
            return []
        # Это значит что процесс не запущен

        result.append(
            [reg_value['value'] for reg_value in gdb_wrapper._parse_log(log, 'result')['payload']['register-values']])
        if self._flags_name in self._registers:
            result[1][index_of_flags] = self.get_flags()
        return result

    @no_response()
    def write(self, command, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        if command.strip() == "q":
            self.gdb_ctrl.exit()
            return ""
        log = self.gdb_ctrl.write(mi_cmd_to_write=command, timeout_sec=timeout_sec)
        return log

    @no_response()
    def quit(self):
        self.gdb_ctrl.exit()


class gdb_wrapper_x86_64(gdb_wrapper):
    def __init__(self, port=None, file=None):
        self.gdb_ctrl = GdbController(["gdb-multiarch", "-q", "--interpreter=mi"])
        self.gdb_ctrl.write("set architecture i386:x86_64")
        self._registers = {'r{}'.format(i) for i in range(8, 16)}
        self._registers.update({'rax', 'rdi', 'rsi', 'rdx', 'rcx', 'rbx', 'rsp', 'rbp', 'rip', 'eflags'})
        # self._registers.update({'eax', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'esp', 'ebp', 'eip'})
        self._flags_name = 'eflags'
        super().__init__(port, file)

    @gdb_wrapper.no_response()
    def get_flags(self, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        log = self.gdb_ctrl.write("print ${}".format(self._flags_name), timeout_sec)
        _, _, values = self._parse_log(log, 'console')['payload'].partition(' = ')
        result = {}
        all_flags = values.rstrip('\\n').strip('][').split()
        for flag_value in all_flags:
            flag_name, _, value = flag_value.partition('=')
            if value == '':
                value = 1
            result[flag_name] = value
        return result


class gdb_wrapper_arm(gdb_wrapper):
    def __init__(self, port=None, file=None):
        self.gdb_ctrl = GdbController(["gdb-multiarch", "-q", "--interpreter=mi"])
        self.gdb_ctrl.write("set architecture arm")
        self._registers = {'r{}'.format(i) for i in range(13)}
        self._registers.update({'sp', 'lr', 'pc', 'cpsr'})
        self._flags_name = 'cpsr'
        super().__init__(port, file)

    @gdb_wrapper.no_response()
    def get_flags(self, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        log = self.gdb_ctrl.write("print ${}".format(self._flags_name), timeout_sec)
        _, _, values = gdb_wrapper._parse_log(log, 'console')['payload'].partition(' = ')

        all_flags = [['M', 0], ['M', 1], ['M', 2], ['M', 3], ['M', 4], 'T', 'F', 'I', 'A', 'E', ['IT', 2], ['IT', 3],
                     ['IT', 4], ['IT', 5], ['IT', 6], ['IT', 7], ['GE', 0], ['GE', 1], ['GE', 2], ['GE', 3], ['DNM', 0],
                     ['DNM', 1], ['DNM', 2], ['DNM', 3], 'J', ['IT', 0], ['IT', 1], 'Q', 'V', 'C', 'Z', 'N']

        return gdb_wrapper._parse_flags(int(values.rstrip('\\n')), all_flags)


class gdb_wrapper_avr(gdb_wrapper):
    def __init__(self, port=None, file=None):
        self.gdb_ctrl = GdbController(["avr-gdb", "-q", "--interpreter=mi"])
        self._registers = {'r{}'.format(i) for i in range(32)}
        self._registers.update({'SP', 'PC', 'SREG'})
        self._flags_name = 'SREG'
        super().__init__(port, file)

    @gdb_wrapper.no_response()
    def get_flags(self, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        all_flags = ['C', 'Z', 'N', 'V', 'S', 'H', 'T', 'I']
        log = self.gdb_ctrl.write("print ${}".format(self._flags_name), timeout_sec)
        _, _, values = gdb_wrapper._parse_log(log, 'console')['payload'].partition(' = ')

        return gdb_wrapper._parse_flags(int(values.rstrip('\\n')), all_flags)


# basic test to be improved and should be output in a separate file
if __name__ == '__main__':
    from demo_debug.py_demo.as_run import as_runner
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

    gdbrun = gdb_wrapper_x86_64(qmrun.dbg_port, qmrun.cur_exec)
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
