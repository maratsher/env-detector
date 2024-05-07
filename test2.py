import numpy as np
import cv2
from scipy.stats import skew
from skimage.feature import graycomatrix, graycoprops



_low_threshold = 0.005
_high_threshold = 0.995

def calculate(frame, bboxes):
    input_img_quantized = (frame / 16).astype(np.uint8)

    glcm = graycomatrix(input_img_quantized, distances=[1], angles=[0], levels=16, symmetric=True, normed=True)
    
    contrast_total = graycoprops(glcm, 'contrast')[0, 0]
    homogeneity_total = graycoprops(glcm, 'homogeneity')[0, 0]
    energy_total = graycoprops(glcm, 'energy')[0, 0]
    correlation_total = graycoprops(glcm, 'correlation')[0, 0]

    metrics = []
    for x_min, y_min, x_max, y_max in bboxes:
        sub_img = input_img_quantized[y_min:y_max, x_min:x_max]
        if sub_img.size == 0:
            continue  # Пропускаем пустые рамки
        glcm_sub = graycomatrix(sub_img, distances=[1], angles=[0], levels=16, symmetric=True, normed=True)
        metrics.append([
            graycoprops(glcm_sub, 'contrast')[0, 0],
            graycoprops(glcm_sub, 'homogeneity')[0, 0],
            graycoprops(glcm_sub, 'energy')[0, 0],
            graycoprops(glcm_sub, 'correlation')[0, 0]
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

# Image dimensions and settings
width = 2448
height = 2048
rectangles = [[1242, 240, 1744, 852], [10, 10, 200, 200]]

# Create a greyscale image with all pixels initially set to 0
image = np.zeros((height, width), dtype=np.uint8)

# Set pixels within specified rectangles to 255
for rect in rectangles:
    x1, y1, x2, y2 = rect
    image[y1:y2, x1:x2] = 255
    
print(calculate(image, rectangles))
    
    
