from env_detector.metrics import BaseMetric

import numpy as np
import cv2
from scipy.stats import skew


class TextureMetric(BaseMetric):

    def __init__(self) -> None:
        super().__init__()

    def calculate(self, frame) -> tuple:
        histogram = cv2.calcHist([frame], [0], None, [256], [0, 256])
        histogram = histogram / np.sum(histogram)

        entropy = -np.sum(histogram[histogram > 0]
                          * np.log2(histogram[histogram > 0]))
        skewness = skew(frame.flatten())

        return entropy, skewness
