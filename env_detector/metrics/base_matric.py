import abc
import time

import numpy as np

def count_exec_time(method):
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = method(self, *args, **kwargs)
        end_time = time.time()
        self._exec_time = end_time - start_time
        return result
    return wrapper

class BaseMetric(metaclass=abc.ABCMeta):
    
    def __init__(self, name="BaseMetric", win_size=0) -> None:
        self._name = name
        self._exec_time = 0
        
        self._win_size = win_size
        self._n_val = 0
        self._window = np.empty((0, 1), dtype=np.float)
        
    @property
    def exec_time(self):
        return self._exec_time
        
    @property
    def name(self):
        return self._name

    @abc.abstractmethod
    def calculate(self, frame, bboxes=None) -> dict:
        return None
        
    def _slide_window(self, new_element):        
        if self._n_val <= self._win_size:
            self._window = np.vstack((self._window, new_element))
        else:
            self._window[:-1] = self._window[1:]
            self._window[-1] = new_element
            
        return np.mean(self._window)
    