from env_detector.metrics import BaseMetric, count_exec_time

import numpy as np
import cv2
# from scipy.stats import skew


class TextureMetric(BaseMetric):
    pass
    # def __init__(self, name, win_size=0) -> None:
    #     super().__init__(name, win_size)

    # @count_exec_time
    # def calculate(self, frame, bboxes):        
    #     mask = np.zeros(frame.shape[:2], dtype=bool)
    #     for x_min, y_min, x_max, y_max in bboxes:
    #         mask[y_min:y_max, x_min:x_max] = True
        
    #     mask_out = ~mask

    #     def calc_stats(f, m=None):
    #         if m is not None:
    #             f = f[m]
    #         if f.size == 0:
    #             return np.nan, np.nan  # Возвращаем NaN, если нет пикселей
    #         hist = cv2.calcHist([f], [0], None, [256], [0, 256])
    #         hist = hist / np.sum(hist)
    #         entropy = -np.sum(hist[hist > 0] * np.log2(hist[hist > 0]))
    #         skewness = skew(f.flatten())
    #         return entropy, skewness

    #     entropy_total, skewness_total = calc_stats(frame)
        
    #     if bboxes == []:
    #         entropy_inside, skewness_inside = None, None
    #         entropy_outside, skewness_outside = None, None
    #     else:    
    #         entropy_inside, skewness_inside = calc_stats(frame, mask)
    #         entropy_outside, skewness_outside = calc_stats(frame, mask_out)

    #     return {
    #         "entropy_total": entropy_total, "skewness_total": skewness_total,
    #         "entropy_cars": entropy_inside, "skewness_cars": skewness_inside,
    #         "entropy_back": entropy_outside, "skewness_back": skewness_outside
    #     }
