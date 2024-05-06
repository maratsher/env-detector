from env_detector.metrics import BaseMetric, count_exec_time

import numpy as np
from skimage.feature import greycomatrix, greycoprops


class GLCMMetric(BaseMetric):

    def __init__(self, name, win_size=0) -> None:
        super().__init__(name, win_size)

    @count_exec_time
    def calculate(self, frame, bboxes):
        input_img_quantized = (frame / 16).astype(np.uint8)

        glcm = greycomatrix(input_img_quantized, distances=[1], angles=[0], levels=16, symmetric=True, normed=True)
        
        contrast_total = greycoprops(glcm, 'contrast')[0, 0]
        homogeneity_total = greycoprops(glcm, 'homogeneity')[0, 0]
        energy_total = greycoprops(glcm, 'energy')[0, 0]
        correlation_total = greycoprops(glcm, 'correlation')[0, 0]
        
        if bboxes == []:
            mean_metrics = [None, None, None, None]
        else:
            metrics = []
            for x_min, y_min, x_max, y_max in bboxes:
                sub_img = input_img_quantized[y_min:y_max, x_min:x_max]
                if sub_img.size == 0:
                    continue  # Пропускаем пустые рамки
                glcm_sub = greycomatrix(sub_img, distances=[1], angles=[0], levels=16, symmetric=True, normed=True)
                metrics.append([
                    greycoprops(glcm_sub, 'contrast')[0, 0],
                    greycoprops(glcm_sub, 'homogeneity')[0, 0],
                    greycoprops(glcm_sub, 'energy')[0, 0],
                    greycoprops(glcm_sub, 'correlation')[0, 0]
                ])

            if metrics:
                mean_metrics = np.mean(metrics, axis=0)
            else:
                mean_metrics = [np.nan, np.nan, np.nan, np.nan]

        results = {
            "contrast_total": contrast_total, "homogeneity_total": homogeneity_total, "energy_total": energy_total, "correlation_total": correlation_total,
            "contrast_cars": mean_metrics[0], "homogeneity_cars": mean_metrics[1], "energy_cars": mean_metrics[2], "correlation_cars": mean_metrics[3]
        }

        return results
