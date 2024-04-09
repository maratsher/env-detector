import numpy as np
import cv2

from env_detector.metrics import BaseMetric, count_exec_time


class SharpnessMetric(BaseMetric):

    def __init__(self, name, win_size=0) -> None:
        super().__init__(name, win_size)

    @count_exec_time
    def calculate(self, frame):
        laplacian = cv2.Laplacian(frame, cv2.CV_64F)
        return {"laplacian" : laplacian.var(), }