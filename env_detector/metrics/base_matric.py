import abc

class BaseMetric(metaclass=abc.ABCMeta):
    
    def __init__(self, name="BaseMetric") -> None:
        self._name = name
        
    @property
    def get_name(self):
        return self._name

    @abc.abstractmethod
    def calculate(self, frame) -> tuple:
        return None