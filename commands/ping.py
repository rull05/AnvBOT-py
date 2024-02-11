import psutil
import platform
import os
from datetime import timedelta


from utils import MessageSerialize
from src.command import CommandBase

class Ping(CommandBase):
    prefix: str = '!'
    pattern: str = 'ping'
    desc: str = 'Get system information'

    def execute(self, msg: MessageSerialize):
        msg.reply(get_system_info())


def get_system_info():
    uname = platform.uname()
    os_name = platform.system()
    kernel = uname.release
    uptime = timedelta(seconds=int(psutil.boot_time()))
    packages = len(os.listdir('/var/lib/dpkg/info/'))
    shell = os.getenv('SHELL')
    terminal = os.getenv('TERM')
    cpu = platform.processor()
    memory = psutil.virtual_memory()
    memory = f'{convert_bytes_to_gb(memory.used):.2f}GB / {convert_bytes_to_gb(memory.total):.2f}GB'
    return f'OS: {os_name} {uname.version}\nKernel: {kernel}\nUptime: {uptime}\nPackages: {packages} (dpkg)\nShell: {shell}\nTerminal: {terminal}\nCPU: {cpu}\nMemory: {memory}'

    
    


def convert_bytes_to_gb(_bytes: int) -> float:
    return _bytes / (1024.0 ** 3)  # Convert bytes to GB