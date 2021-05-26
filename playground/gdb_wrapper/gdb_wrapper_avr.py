from pygdbmi.constants import DEFAULT_GDB_TIMEOUT_SEC
from pygdbmi.gdbcontroller import GdbController

from playground.gdb_wrapper.gdb_wrapper import gdb_wrapper


class gdb_wrapper_avr(gdb_wrapper):
    def __init__(self, port=None, file=None):
        self.gdb_ctrl = GdbController(["avr-gdb", "-q", "--interpreter=mi"])
        self._registers = {'r{}'.format(i) for i in range(32)}
        self._registers.update({'SP', 'PC', 'SREG'})
        self._flags_name = 'SREG'
        self._flag_to_pos = {'C': [0], 'Z': [1], 'N': [2], 'V': [3], 'S': [4], 'H': [5], 'T': [6], 'I': [7]}

        super().__init__(port, file)

    @gdb_wrapper.no_response()
    def get_flags(self, timeout_sec=DEFAULT_GDB_TIMEOUT_SEC):
        all_flags = ['C', 'Z', 'N', 'V', 'S', 'H', 'T', 'I']
        log = self.gdb_ctrl.write("print ${}".format(self._flags_name), timeout_sec)
        _, _, values = gdb_wrapper._parse_log(log, 'console')['payload'].partition(' = ')

        return gdb_wrapper._parse_flags(int(values.rstrip('\\n')), all_flags)
