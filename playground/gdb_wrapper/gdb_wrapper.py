from pygdbmi.constants import GdbTimeoutError, DEFAULT_GDB_TIMEOUT_SEC
from playground.gdb_wrapper.gdb_error import gdb_error
from typing import Union, List


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

    def __init__(self, port: int = None, file: str = None):
        self.breakpoints = {}
        self.__all_regs = set()
        self.__changed_regs = set()
        self.pid = self.gdb_ctrl.gdb_process.pid
        self.need_dump = False
        if port is not None:
            self.connect_to_port(port)
        if file is not None:
            self.gdb_ctrl.write("file " + file)

    @staticmethod
    def _parse_log(log, type: str):
        for el in log:
            if el['type'] == type:
                return el

    @staticmethod
    def _parse_flags(flags_value: int, all_flags: List):
        result = {}
        for i in range(len(all_flags)):
            flag_name = all_flags[i]
            if isinstance(flag_name, list):
                if flag_name[0] in result:
                    result[flag_name[0]] += (flags_value >> i & 1) << flag_name[1]
                else:
                    result[flag_name[0]] = (flags_value >> i & 1) << flag_name[1]
            else:
                result[flag_name] = flags_value >> i & 1
        return result

    @no_response()
    def _get_updated_flags_reg(self, flag_name: str, flag_value: int, timeout_sec: int = DEFAULT_GDB_TIMEOUT_SEC):
        log = self.gdb_ctrl.write("p/t ${}".format(self._flags_name), timeout_sec)
        _, _, value_string = gdb_wrapper._parse_log(log, 'console')['payload'].partition(' = ')
        value_string = value_string.rstrip('\\n')

        value_string = '0' * (64 - len(value_string)) + value_string

        if flag_name not in self._flag_to_pos:
            raise KeyError('No such flag')

        value_list = list(value_string)

        for index, pos_in_reg in enumerate(self._flag_to_pos[flag_name]):
            value_list[- pos_in_reg - 1] = chr(48 + ((flag_value >> index) & 1))

        value_string = ''.join(value_list)
        return int(value_string, 2)

    @no_response()
    def connect_to_port(self, port: int, timeout_sec: int = DEFAULT_GDB_TIMEOUT_SEC):
        log = self.gdb_ctrl.write("target extended-remote localhost:" + str(port), timeout_sec)
        return log

    @no_response()
    def step_over(self, timeout_sec: int = DEFAULT_GDB_TIMEOUT_SEC):
        log = self.gdb_ctrl.write("-exec-next", timeout_sec)
        return log

    @no_response()
    def step_in(self, timeout_sec: int = DEFAULT_GDB_TIMEOUT_SEC):
        log = self.gdb_ctrl.write("-exec-step", timeout_sec)
        return log

    # Если у нас только внешняя функция, то он ничего не сделает
    @no_response()
    def step_out(self, timeout_sec: int = DEFAULT_GDB_TIMEOUT_SEC):
        log = self.gdb_ctrl.write("-exec-finish", timeout_sec)
        return log

    @no_response()
    def get_stack(self, timeout_sec: int = DEFAULT_GDB_TIMEOUT_SEC):
        log = self.gdb_ctrl.write("-stack-list-frames", timeout_sec)
        if gdb_wrapper._parse_log(log, 'result')['message'] == 'error':
            return {}
        return gdb_wrapper._parse_log(log, 'result')['payload']

    @no_response()
    def get_registers(self, timeout_sec: int = DEFAULT_GDB_TIMEOUT_SEC):
        # надо проверить что процесс запущен
        result = []
        log = self.gdb_ctrl.write("-data-list-register-names", timeout_sec)
        indexes_of_registers = [index for index, elem in
                                enumerate(gdb_wrapper._parse_log(log, 'result')['payload']['register-names']) if
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
    def set_breakpoint(self, line_number: int, timeout_sec: int = DEFAULT_GDB_TIMEOUT_SEC):
        log = self.gdb_ctrl.write('-break-insert --line {}'.format(line_number), timeout_sec)
        if gdb_wrapper._parse_log(log, 'result')['message'] != 'done':
            return log
        self.breakpoints[line_number] = gdb_wrapper._parse_log(log, 'result')['payload']['bkpt']['number']
        return log

    @no_response()
    def remove_breakpoint(self, line_number: int, timeout_sec: int = DEFAULT_GDB_TIMEOUT_SEC):
        if line_number in self.breakpoints:
            log = self.gdb_ctrl.write('-break-delete {}'.format(self.breakpoints[line_number]), timeout_sec)
            if gdb_wrapper._parse_log(log, 'result')['message'] == 'done':
                del self.breakpoints[line_number]
            return log
        return [{'type': 'result', 'message': 'error',
                 'payload': {'msg': 'No breakpoint at line number {}'.format(line_number)}, 'token': None,
                 'stream': 'stdout'}]

    @no_response()
    def write(self, command: Union[str, List[str]], timeout_sec: int = DEFAULT_GDB_TIMEOUT_SEC):
        if command.strip() == "q":
            self.gdb_ctrl.exit()
            return []
        log = self.gdb_ctrl.write(mi_cmd_to_write=command, timeout_sec=timeout_sec)
        return log

    @no_response()
    def set_register(self, reg_name: str, value: int, timeout_sec: int = DEFAULT_GDB_TIMEOUT_SEC):
        if len(self.__all_regs) == 0:
            log = self.gdb_ctrl.write("-data-list-register-names", timeout_sec)
            self.__all_regs = gdb_wrapper._parse_log(log, 'result')['payload']['register-names']
        if reg_name not in self.__all_regs and reg_name not in self._flag_to_pos:
            raise KeyError('No such register')
        is_flag = reg_name in self._flag_to_pos
        if is_flag:
            flag_name = reg_name
            reg_name = self._flags_name

        if reg_name not in self.__changed_regs:
            log = self.gdb_ctrl.write('-var-create {0} * ${0}'.format(reg_name))
            if self._parse_log(log, 'result')['message'] == 'error':
                raise gdb_error(log, 'Error in creating a variable for a register')
            self.__changed_regs.add(reg_name)

        if is_flag:
            value = self._get_updated_flags_reg(flag_name, int(value), timeout_sec)
        return self.gdb_ctrl.write('-var-assign {} {}'.format(reg_name, value))

    @no_response()
    def quit(self):
        self.gdb_ctrl.exit()
