import numpy as np
import cv2

from env_detector.metrics import BaseMetric, count_exec_time


class RMSMetric(BaseMetric):

    def __init__(self, name, win_size=0) -> None:
        super().__init__(name, win_size)
        self._low_threshold = 0.005
        self._high_threshold = 0.995

    @count_exec_time
    def calculate(self, frame) -> tuple:
        grad_x = cv2.Sobel(frame, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(frame, cv2.CV_64F, 0, 1, ksize=3)

        rms_gradient = np.sqrt(np.mean(grad_x**2 + grad_y**2))

        return { "rms": rms_gradient, }
