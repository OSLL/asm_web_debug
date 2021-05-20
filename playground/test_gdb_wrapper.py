def compile_and_start(dir_path, file_name, arch):
    from demo_debug.py_demo.as_run import as_runner
    from demo_debug.py_demo.ld_run import ld_runner
    from demo_debug.py_demo.qemu_run import qemu_runner

    s_path = "{0}/{1}.s".format(dir_path, file_name)
    o_path = "{0}/{1}.o".format(dir_path, file_name)
    out_path = "{0}/{1}.out".format(dir_path, file_name)

    asrun = as_runner(arch)
    resp = asrun.run(s_path, o_path)
    print(str(resp.stdout)[2:-1])
    print(str(resp.stderr)[2:-1])
    if resp.returncode != 0:
        exit(resp.returncode)

    ldrun = ld_runner(arch)
    resp = ldrun.run(o_path, out_path)
    print(str(resp.stdout)[2:-1])
    print(str(resp.stderr)[2:-1])
    if resp.returncode != 0:
        exit(resp.returncode)

    qmrun = qemu_runner(arch)
    qmrun.run(out_path)
    return qmrun


def run(gdb_run):
    print('go')
    while True:
        gcmd = input()
        if gcmd == 'info reg':
            print(gdb_run.get_registers())
        elif gcmd == 'info stack':
            print(gdb_run.get_stack())
        elif gcmd.startswith('breakpoint'):
            print(gdb_run.set_breakpoint(int(gcmd.split()[1])))
        elif gcmd.startswith('remove breakpoint'):
            print(gdb_run.remove_breakpoint(int(gcmd.split()[2])))
        elif gcmd == 'n':
            print(gdb_run.step_over())
        else:
            resp = gdb_run.write(gcmd, timeout_sec=1)
            print(resp, end='')
        if gcmd == 'q':
            break


def get_gdb_wrapper(dir_path, file_name, arch):
    qm_run = compile_and_start(dir_path, file_name, arch)
    if arch == 'x86_64':
        from gdb_wrapper.gdb_wrapper_x86 import gdb_wrapper_x86_64
        return gdb_wrapper_x86_64(qm_run.dbg_port, qm_run.cur_exec)
    elif arch == 'arm':
        from gdb_wrapper.gdb_wrapper_arm import gdb_wrapper_arm
        return gdb_wrapper_arm(qm_run.dbg_port, qm_run.cur_exec)
    elif arch == 'avr':
        from gdb_wrapper.gdb_wrapper_avr import gdb_wrapper_avr
        return gdb_wrapper_avr(qm_run.dbg_port, qm_run.cur_exec)


if __name__ == '__main__':
    gdb_wrapper = get_gdb_wrapper('demo_debug/demos', 'demo_helloworld.arm', 'arm')
    run(gdb_wrapper)
