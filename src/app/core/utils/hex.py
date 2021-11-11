def hexdump(buffer):
    lines = []

    for line in range(0, len(buffer), 16):
        block = buffer[line : line + 16]
        addr = "{:08X}".format(int(hex(line), 16))
        hexed = " ".join(
            ["{:02X}".format(ord(x)) if ord(x) <= 127 else " 00" for x in block]
        )
        chars = "".join([x if ord(x) <= 127 and ord(x) >= 20 else "." for x in block])
        lines.append("{} \n {} \n {}".format(addr, hexed, chars))

    return "\n".join(lines)
