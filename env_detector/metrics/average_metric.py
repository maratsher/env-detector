import numpy as np

from env_detector.metrics import BaseMetric, count_exec_time


class AverageMetric(BaseMetric):

    def __init__(self, name) -> None:
        super().__init__(name)
        self._low_threshold = 0.005

    @count_exec_time
    def calculate(self, frame):
        return {"mean " : np.mean(frame), }
