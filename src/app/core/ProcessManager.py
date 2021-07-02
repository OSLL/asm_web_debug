



from app.core.QemuUserProcess import QemuUserProcess


class ProcessManager:
    # 'process_id' : [new QemuUserProcess, new gdb wrapper]
    process_map = {}


    def __init__(cls, max_num_of_process = 1000, min_port = 10000) -> None:
        cls.max_num_of_process = max_num_of_process
        cls.min_port = min_port


    # process_id <--- hash(user_id + code_id)
    def exec(cls, path, process_id, arch, debug):
        qemu_process  = None
        gdb_process   = None

        port = 0 #gen_port()

        qemu_process = QemuUserProcess(path, arch, debug)

        #if debug:
        #    gdb_process = gdb_wrapper(port)

        if cls.process_map.get(process_id, None) != None:
            cls.terminate(process_id)

        cls.process_map[process_id] = [qemu_process, gdb_process]

        return qemu_process.run(port)
        
        # run gdb...


    def terminate(cls, process_id):
        process = cls.process_map.get(process_id, None)
        if process == None:
            return False

        # terminate....
        return True
        

    def status(cls, process_id):
        process = cls.process_map.get(process_id, None)
        if process == None:
            return None
        
        return process[0].get_state()



    def debug(cls, command):
        pass
