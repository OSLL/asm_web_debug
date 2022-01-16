import string
from collections import namedtuple

Result = namedtuple("Result", ["status", "values"])
ExecAsync = namedtuple("ExecAsync", ["status", "values"])
StatusAsync = namedtuple("StatusAsync", ["status", "values"])
Notification = namedtuple("Notification", ["status", "values"])
DebuggerOutput = namedtuple("DebuggerOutput", ["line"])
TargetOutput = namedtuple("TargetOutput", ["line"])
LogOutput = namedtuple("LogOutput", ["line"])


class Parser:
    def __init__(self, s):
        self.string = s
        self.pos = 0

    def next(self):
        ch = self.peek()
        if ch is not None:
            self.pos += 1
        return ch

    def peek(self):
        if self.pos >= len(self.string):
            return None
        return self.string[self.pos]

    def consume(self, ch):
        if self.next() != ch:
            raise RuntimeError(f"invalid consume, expected {ch!r}")
        return ch

    def skip(self, ch):
        if self.peek() == ch:
            self.next()
            return True
        return False

    def parse_result(self):
        status = self.parse_token()
        if self.skip(","):
            values = self.parse_dict_interior()
        else:
            values = {}
        return status, values

    def parse_token(self):
        result = []
        while self.peek() in set(string.ascii_letters + string.digits + "_-"):
            result.append(self.next())
        return "".join(result)

    def parse_cstring(self):
        result = [self.consume('"')]
        while self.peek() != '"':
            if self.peek() == "\\":
                result.append(self.next())
                if self.peek() != '"':
                    continue
            result.append(self.next())
        result.append(self.consume('"'))

        return eval("".join(result))

    def parse_list(self):
        self.consume("[")
        result = self.parse_list_interior()
        self.consume("]")
        return result

    def parse_list_interior(self):
        result = []
        while self.peek() not in [None, "]"]:
            result.append(self.parse_value())
            self.skip(",")
        return result

    def parse_dict(self):
        self.consume("{")
        result = self.parse_dict_interior()
        self.consume("}")
        return result

    def parse_dict_interior(self):
        result = {}
        while self.peek() not in [None, "}"]:
            key = self.parse_token()
            self.consume("=")
            value = self.parse_value()
            result[key] = value
            self.skip(",")
        return result

    def parse_value(self):
        if self.peek() == '"':
            return self.parse_cstring()
        elif self.peek() == "[":
            return self.parse_list()
        elif self.peek() == "{":
            return self.parse_dict()
        raise RuntimeError("invalid parse_value")


def parse_gdb_response(line):
    line = line.strip()
    if line == "(gdb)" or line == "":
        return None

    kind = line[0]
    parser = Parser(line[1:])

    if kind == "^":
        return Result(*parser.parse_result())
    elif kind == "*":
        return ExecAsync(*parser.parse_result())
    elif kind == "+":
        return StatusAsync(*parser.parse_result())
    elif kind == "=":
        return Notification(*parser.parse_result())
    elif kind == "~":
        return DebuggerOutput(parser.parse_cstring())
    elif kind == "@":
        return TargetOutput(parser.parse_cstring())
    elif kind == "&":
        return LogOutput(parser.parse_cstring())
    else:
        raise RuntimeError(f"invalid gdb response: {line!r}")
