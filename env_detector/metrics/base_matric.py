import abc
import time

def count_exec_time(method):
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = method(self, *args, **kwargs)
        end_time = time.time()
        self._exec_time = end_time - start_time
        return result
    return wrapper

class BaseMetric(metaclass=abc.ABCMeta):
    
    def __init__(self, name="BaseMetric") -> None:
        self._name = name
        self._exec_time = 0
        
    @property
    def exec_time(self):
        return self._exec_time
        
    @property
    def name(self):
        return self._name

    @abc.abstractmethod
    def calculate(self, frame) -> dict:
        return None