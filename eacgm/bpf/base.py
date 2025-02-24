class BPFState:
    task:str
    pid:int
    cpu:int
    timestamp:int
    message:str

    def __init__(self) -> None:
        self.task = None
        self.pid = None
        self.cpu = None
        self.timestamp = None
        self.message = None
        return
    
    def is_none(self) -> bool:
        return self.task is None

    def __repr__(self) -> str:
        info = f"BPFState {self.task} {self.pid} { self.cpu} {self.timestamp} {self.message}"
        return info

class BaseBPF:
    def __init__(self, name:str) -> None:
        self.name = name
        return

    def attach_uprobe(self, exe_path:str, exe_sym:str, bpf_func:str) -> bool:
        raise NotADirectoryError

    def attach_uretprobe(self, exe_path:str, exe_sym:str, bpf_func:str) -> bool:
        raise NotADirectoryError
    
    def cleanup(self) -> None:
        raise NotADirectoryError
    
    def trace_ebpf(self) -> BPFState:
        raise NotADirectoryError