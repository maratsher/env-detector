import numpy as np
import cv2

from env_detector.metrics import BaseMetric


class DynamicRangeMetric(BaseMetric):

    def __init__(self) -> None:
        super().__init__()
        self._low_threshold = 0.005
        self._high_threshold = 0.995

    def calculate(self, frame) -> tuple:
        histogram = cv2.calcHist([frame], [0], None, [256], [0, 256])
        histogram /= histogram.sum()

        cumulative_distribution = histogram.cumsum()

        lower_bound = np.searchsorted(
            cumulative_distribution, self._low_threshold)
        upper_bound = np.searchsorted(
            cumulative_distribution, self._high_threshold)

        return (int(upper_bound - lower_bound), )
