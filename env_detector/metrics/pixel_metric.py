import numpy as np
import cv2

from env_detector.metrics import BaseMetric, count_exec_time


class PixelMetric(BaseMetric):

    def __init__(self, name, win_size=0) -> None:
        super().__init__(name, win_size)
        self._low_threshold = 0.005

    @count_exec_time
    def calculate(self, frame):
        histogram = cv2.calcHist([frame], [0], None, [256], [0, 256])
        histogram_norm = histogram.ravel()/histogram.max()
        std_deviation = np.std(histogram_norm)
        return {"mean" : np.mean(frame), "std_hist": std_deviation}
