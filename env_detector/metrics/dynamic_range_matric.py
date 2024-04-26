import numpy as np
import cv2

from env_detector.metrics import BaseMetric, count_exec_time


class DynamicRangeMetric(BaseMetric):

    def __init__(self, name, win_size=0) -> None:
        super().__init__(name, win_size)
        self._low_threshold = 0.005
        self._high_threshold = 0.995

    @count_exec_time
    def calculate(self, frame, bboxes):
        mask = np.zeros(frame.shape[:2], dtype=bool)
        for x_min, y_min, x_max, y_max in bboxes:
            mask[y_min:y_max, x_min:x_max] = True
        
        mask_out = ~mask

        def calc_range(f, m=None):
            if m is not None:
                f = f[m]
            if f.size == 0:
                return np.nan  # Возвращаем NaN, если нет пикселей
            histogram = cv2.calcHist([f], [0], None, [256], [0, 256])
            histogram /= histogram.sum()
            cumulative_distribution = histogram.cumsum()
            lower_bound = np.searchsorted(cumulative_distribution, self._low_threshold)
            upper_bound = np.searchsorted(cumulative_distribution, self._high_threshold)
            return int(upper_bound - lower_bound)

        range_total = calc_range(frame)
        range_inside = calc_range(frame, mask)
        range_outside = calc_range(frame, mask_out)

        return {
            "range_total": range_total,
            "range_cars": range_inside,
            "range_back": range_outside
        }
