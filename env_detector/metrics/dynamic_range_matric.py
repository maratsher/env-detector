import numpy as np
import cv2

from env_detector.metrics import BaseMetric, count_exec_time


class DynamicRangeMetric(BaseMetric):

    def __init__(self, name, win_size=0) -> None:
        super().__init__(name, win_size)
        self._low_threshold = 0.005
        self._high_threshold = 0.995

    @count_exec_time
    def calculate(self, frame):
        histogram = cv2.calcHist([frame], [0], None, [256], [0, 256])
        histogram /= histogram.sum()

        cumulative_distribution = histogram.cumsum()

        lower_bound = np.searchsorted(
            cumulative_distribution, self._low_threshold)
        upper_bound = np.searchsorted(
            cumulative_distribution, self._high_threshold)

        return {"range": int(upper_bound - lower_bound) }
