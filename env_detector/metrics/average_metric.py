import numpy as np

from env_detector.metrics import BaseMetric


class AverageMetric(BaseMetric):

    def __init__(self) -> None:
        super().__init__()
        self._low_threshold = 0.005

    def calculate(self, frame) -> tuple:
        return (np.mean(frame), )
