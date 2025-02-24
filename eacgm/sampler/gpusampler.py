import time
import pynvml
from typing import List

from .base import BaseSampler

class GPUSamplerState:
    def __init__(self) -> None:
        super().__init__()
        self.gpu:int = None
        self.name:str = None
        self.sm:int = None
        self.totMem:int = None
        self.usedMem:int = None
        self.enc:int = None
        self.dec:int = None
        self.tmp:int = None
        self.fan:int = None
        self.usedPower:float = None
        self.totPower:float = None
        return
    
    def __repr__(self) -> str:
        info = f"GPUSamplerState {self.gpu} {self.name} {self.sm} {self.usedMem} {self.totMem} {self.enc} {self.dec} {self.tmp} {self.fan} {self.usedPower} {self.totPower}"
        return info

class GPUSampler(BaseSampler):
    def __init__(self) -> None:
        super().__init__(name="GPUSampler")
        pynvml.nvmlInit()
        self.deviceCount:int = pynvml.nvmlDeviceGetCount()
        self.nvDevices:List  = [pynvml.nvmlDeviceGetHandleByIndex(idx) for idx in range(self.deviceCount)]
        return
    
    def run(self) -> None:
        return
    
    def sample(self) -> List[GPUSamplerState]:
        samples = []
        for gpu_idx in range(self.deviceCount):
            gpu_handle = self.nvDevices[gpu_idx]
            try:
                sample = GPUSamplerState()
                sample.gpu = pynvml.nvmlDeviceGetIndex(gpu_handle)
                sample.name = pynvml.nvmlDeviceGetName(gpu_handle)
                sample.sm = pynvml.nvmlDeviceGetUtilizationRates(gpu_handle).gpu
                mem_info = pynvml.nvmlDeviceGetMemoryInfo(gpu_handle)
                sample.totMem = mem_info.total
                sample.usedMem = mem_info.used
                sample.enc = pynvml.nvmlDeviceGetEncoderUtilization(gpu_handle)[0]
                sample.dec = pynvml.nvmlDeviceGetDecoderUtilization(gpu_handle)[0]
                sample.tmp = pynvml.nvmlDeviceGetTemperature(gpu_handle, pynvml.NVML_TEMPERATURE_GPU)
                sample.fan = pynvml.nvmlDeviceGetFanSpeed(gpu_handle)
                sample.usedPower = pynvml.nvmlDeviceGetPowerUsage(gpu_handle) / 1000.0
                sample.totPower = pynvml.nvmlDeviceGetPowerManagementLimit(gpu_handle) / 1000.0
                samples.append(sample)
            except pynvml.NVMLError as e:
                print(e)
                pass
        return samples

    def close(self) -> None:
        pynvml.nvmlShutdown()
        return