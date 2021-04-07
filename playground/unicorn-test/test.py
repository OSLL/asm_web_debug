from __future__ import print_function
import os
from unicorn import *
from unicorn.x86_const import *

##objcopy --dump-section .text=only_code a.out 


x86_code32 = b"\x41\x4a" #inc ecx dec edx

MEM_MAPPING = 0x100000
MEM_MAPPING_STACK = 0x110000

def hook_code(uc, address, size, user_data):
    print(">>> Tracing instruction at 0x%x, instruction size = 0x%x" %(address, size))
    r_eax = mu.reg_read(UC_X86_REG_EAX)
    print(">>> --- EAX is 0x%x" %r_eax)
    r_esp = mu.reg_read(UC_X86_REG_ESP)
    print(">>> --- ESP is 0x%x" %r_esp)
    #input()


try:
    # Initialize emulator in X86-32bit mode
    mu = Uc(UC_ARCH_X86, UC_MODE_32)

    mu.mem_map(MEM_MAPPING, 1024 * 1024)

    code_len = 0

    with open("only_code", "rb") as file:
        code_len = os.path.getsize('only_code')
        mu.mem_write(MEM_MAPPING, file.read())

    mu.mem_write(MEM_MAPPING_STACK, b'\x00\x00\x11\x00')
    mu.reg_write(UC_X86_REG_ESP, MEM_MAPPING_STACK)
    
    mu.hook_add(UC_HOOK_CODE, hook_code)

    mu.emu_start(MEM_MAPPING, MEM_MAPPING_STACK)

    print("done.")

    r_eax = mu.reg_read(UC_X86_REG_EAX)

    print ("EAX = {0}".format(hex(r_eax)))


except UcError as e:
    print("Exception: {0}".format(e))
