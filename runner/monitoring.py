import asyncio
import time
from runner import metrics
from runner.docker import DockerError
from runner.runner import active_debug_sessions

async def update_resource_usage_gauges(prev: float, old_cpu_usage: float):
    with open("/sys/fs/cgroup/cpuacct/cpuacct.usage") as f:
        cpu_usage = int(f.read().strip()) / 10**9
    with open("/sys/fs/cgroup/memory/memory.usage_in_bytes") as f:
        memory_usage = int(f.read().strip())

    for debug_session in active_debug_sessions:
        try:
            session_cpu_usage = await debug_session.get_total_cpu_time_used()
            session_memory_usage = await debug_session.get_memory_used()
        except DockerError:
            continue

        cpu_usage += session_cpu_usage
        memory_usage += session_memory_usage

    now = time.time()
    metrics.runner_cpu_usage.set((cpu_usage - old_cpu_usage) / (now - prev))
    metrics.runner_memory_usage.set(memory_usage)

    return now, cpu_usage


async def periodically_update_resource_usage_gauges():
    cpu_usage = 0.0
    prev = 0.0
    while True:
        prev, cpu_usage = await update_resource_usage_gauges(prev, cpu_usage)
        await asyncio.sleep(5)
