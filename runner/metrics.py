from prometheus_client import Counter, Gauge, Histogram


running_gdb_processes = Gauge("running_gdb_processes", "Number of currently running GDB processes")

gdb_command_latency = Histogram("gdb_command_latency", "Latency of GDB responses to commands", ("command",))
gdb_command_successes = Counter("gdb_command_successes", "Number of successful GDB commands", ("command",))
gdb_command_failures = Counter("gdb_command_failures", "Number of unsuccessful GDB commands", ("command",))

debug_session_compilation_time = Histogram("debug_session_compilation_time", "Compilation time of programs", ("arch",))
debug_session_container_init_time = Histogram("debug_session_container_init_time", "Container init time", ("arch",))

runner_memory_usage = Gauge("runner_memory_usage", "Runner memory usage in bytes")
runner_cpu_usage = Gauge("runner_cpu_usage", "Runner CPU usage in cores")
