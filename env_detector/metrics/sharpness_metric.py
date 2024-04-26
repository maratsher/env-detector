import numpy as np
import cv2

from env_detector.metrics import BaseMetric, count_exec_time


class SharpnessMetric(BaseMetric):

    def __init__(self, name, win_size=0) -> None:
        super().__init__(name, win_size)

    @count_exec_time
    def calculate(self, frame, bboxes):
        laplacian = cv2.Laplacian(frame, cv2.CV_64F)
        laplacian_var_total = laplacian.var()

        variances = []

        for x_min, y_min, x_max, y_max in bboxes:
            sub_img = frame[y_min:y_max, x_min:x_max]
            if sub_img.size == 0:
                continue 
            sub_laplacian = cv2.Laplacian(sub_img, cv2.CV_64F)
            variances.append(sub_laplacian.var())

        if variances:
            laplacian_var_inside = np.mean(variances)
        else:
            laplacian_var_inside = np.nan 

        results = {
            "laplacian_total": laplacian_var_total,
            "laplacian_cars": laplacian_var_inside
        }

        return results