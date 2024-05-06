import numpy as np
import cv2

from env_detector.metrics import BaseMetric, count_exec_time


class PixelMetric(BaseMetric):

    def __init__(self, name, win_size=0) -> None:
        super().__init__(name, win_size)
        self._low_threshold = 0.005

    @count_exec_time
    def calculate(self, frame, bboxes):
        mask = np.zeros(frame.shape[:2], dtype=bool)
        for x_min, y_min, x_max, y_max in bboxes:
            mask[y_min:y_max, x_min:x_max] = True
        
        mask_out = ~mask
        
        def calc_stats(f, m=None):
            if m is not None:
                f = f[m]
            if f.size == 0:
                return np.nan, np.nan  # Возвращаем NaN, если нет пикселей
            histogram = cv2.calcHist([f], [0], None, [256], [0, 256])
            histogram_norm = histogram.ravel() / histogram.max()
            return np.mean(f), np.std(histogram_norm)
        
        mean_total, std_hist_total = calc_stats(frame)
        if bboxes == []:
            mean_inside, std_hist_inside = None, None
            mean_outside, std_hist_outside = None, None
        else:
            mean_inside, std_hist_inside = calc_stats(frame, mask)
            mean_outside, std_hist_outside = calc_stats(frame, mask_out)
        
        return {
            "mean_total": mean_total, "std_hist_total": std_hist_total,
            "mean_cars": mean_inside, "std_hist_cars": std_hist_inside,
            "mean_back": mean_outside, "std_hist_back": std_hist_outside
        }
