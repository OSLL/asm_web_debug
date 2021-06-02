from pygdbmi.constants import DEFAULT_GDB_TIMEOUT_SEC
from pygdbmi.gdbcontroller import GdbController

from playground.gdb_wrapper.gdb_wrapper import gdb_wrapper


class gdb_wrapper_x86_64(gdb_wrapper):
    def __init__(self, port=None, file=None):
        self.gdb_ctrl = GdbController(["gdb-multiarch", "-q", "--interpreter=mi"])
        self.gdb_ctrl.write("set architecture i386:x86_64")
        self._registers = {'r{}'.format(i) for i in range(8, 16)}
        self._registers.update({'rax', 'rdi', 'rsi', 'rdx', 'rcx', 'rbx', 'rsp', 'rbp', 'rip', 'eflags'})
        # self._registers.update({'eax', 'edi', 'esi', 'edx', 'ecx', 'ebx', 'esp', 'ebp', 'eip'})
        self._flags_name = 'eflags'
        self._flag_to_pos = {'CF': [0], 'PF': [2], 'AF': [4], 'ZF': [6], 'SF': [7], 'TF': [8], 'IF': [9], 'DF': [10],
                             'OF': [11], 'IOPL': [11, 12], 'NT': [14], 'RF': [16], 'VM': [17], 'AC': [18], 'VIF': [19],
                             'VIP': [20], 'ID': [21]}

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
        for flag_name in self._flag_to_pos:
            if flag_name not in result:
                result[flag_name] = 0
        return result
