import os
import psutil


def get_process_memory():
    # return the memory usage in MB
    process = psutil.Process(os.getpid())
    memory_info = process.memory_info()
    mem = memory_info[0] / float(2 ** 20)
    return mem
