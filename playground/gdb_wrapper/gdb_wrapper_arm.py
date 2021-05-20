from pygdbmi.constants import DEFAULT_GDB_TIMEOUT_SEC
from pygdbmi.gdbcontroller import GdbController

from playground.gdb_wrapper.gdb_wrapper import gdb_wrapper


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
