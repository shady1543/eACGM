import time
import pynvml
from typing import List

from .base import BaseSamplerState, BaseSampler

class NVMLSamplerState(BaseSamplerState):
    def __init__(self) -> None:
        super().__init__()
        self.gpu:int = None
        self.sm:int = None
        self.mem:int = None
        self.enc:int = None
        self.dec:int = None
        return
    
    def __repr__(self) -> str:
        info = f"NVMLSamplerState {self.gpu} {self.sm} {self.mem} {self.enc} {self.dec} {super().__repr__()}"
        return info

class NVMLSampler(BaseSampler):
    def __init__(self) -> None:
        super().__init__(name="NVMLSampler")
        pynvml.nvmlInit()
        self.deviceCount:int = pynvml.nvmlDeviceGetCount()
        self.nvDevices:List  = [pynvml.nvmlDeviceGetHandleByIndex(idx) for idx in range(self.deviceCount)]
        return
    
    def run(self) -> None:
        return
    
    def sample(self, time_stamp:float) -> List[NVMLSamplerState]:
        samples = []
        for gpu_idx in range(self.deviceCount):
            gpu_handle = self.nvDevices[gpu_idx]
            try:
                processes = pynvml.nvmlDeviceGetProcessUtilization(gpu_handle, time.time_ns() // 1000 - 1000_000 * time_stamp)
                for process in processes:
                    state = NVMLSamplerState()
                    state.task = None
                    state.pid  = process.pid
                    state.cpu  = None
                    state.timestamp = process.timeStamp
                    state.message   = None
                    state.gpu = gpu_idx
                    state.sm  = process.smUtil
                    state.mem = process.memUtil
                    state.enc = process.encUtil
                    state.dec = process.decUtil
                    samples.append(state)
            except pynvml.NVMLError as e:
                pass
        return samples

    def close(self) -> None:
        pynvml.nvmlShutdown()
        return