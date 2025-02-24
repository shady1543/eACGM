from bcc import BPF
from typing import List

from .base import BPFState, BaseBPF

class BccBPF(BaseBPF):
    def __init__(self, name:str, text:str, cflags:List=[]) -> None:
        super().__init__(name)
        self.bpf = BPF(text=text, cflags=cflags)
        return

    def attach_uprobe(self, exe_path:str, exe_sym:str, bpf_func:str) -> bool:
        self.bpf.attach_uprobe(exe_path, exe_sym, fn_name=bpf_func)
        return

    def attach_uretprobe(self, exe_path:str, exe_sym:str, bpf_func:str) -> bool:
        self.bpf.attach_uretprobe(exe_path, exe_sym, fn_name=bpf_func)
        return
    
    def cleanup(self) -> None:
        self.bpf.cleanup()
        return
    
    def trace_ebpf(self, nonblocking:bool) -> BPFState:
        (task, pid, cpu, _, _, message) = self.bpf.trace_fields(nonblocking)
        state = BPFState()
        if task is not None:
            message = message.decode("utf-8")
            state.task = task.decode("utf-8")
            state.pid  = int(pid)
            state.cpu  = int(cpu)
            state.timestamp = int(message.split("@")[0])
            state.message   = message.split("@")[1:]
        return state