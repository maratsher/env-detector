import numpy as np
import cv2

import abc
import time

def count_exec_time(method):
    def wrapper(self, *args, **kwargs):
        start_time = time.time()
        result = method(self, *args, **kwargs)
        end_time = time.time()
        self._exec_time = end_time - start_time
        return result
    return wrapper

class BaseMetric(metaclass=abc.ABCMeta):
    
    def __init__(self, name="BaseMetric", win_size=0) -> None:
        self._name = name
        self._exec_time = 0
        
        self._win_size = win_size
        self._n_val = 0
        self._window = np.empty((0, 1), dtype=float)
        
    @property
    def exec_time(self):
        return self._exec_time
        
    @property
    def name(self):
        return self._name

    @abc.abstractmethod
    def calculate(self, frame, bboxes=None) -> dict:
        return None
        
    def _slide_window(self, new_element):        
        if self._n_val <= self._win_size:
            self._window = np.vstack((self._window, new_element))
        else:
            self._window[:-1] = self._window[1:]
            self._window[-1] = new_element
            
        return np.mean(self._window)

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
        
        
image = cv2.imread('test_imges/7.png', cv2.IMREAD_GRAYSCALE)

print(image)

print(PixelMetric("test").calculate(image, []))