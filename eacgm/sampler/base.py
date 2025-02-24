class BaseSamplerState:
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
        info = f"{self.task} {self.pid} {self.cpu} {self.timestamp} {self.message}"
        return info

class BaseSampler:
    def __init__(self, name:str) -> None:
        self.name = name
        return
    
    def run(self) -> None:
        raise NotImplementedError
    
    def sample(self):
        raise NotImplementedError

    def close(self) -> None:
        raise NotImplementedError