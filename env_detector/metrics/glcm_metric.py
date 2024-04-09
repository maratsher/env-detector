from env_detector.metrics import BaseMetric, count_exec_time

import numpy as np
from skimage.feature import greycomatrix, greycoprops


class GLCMMetric(BaseMetric):

    def __init__(self, name, win_size=0) -> None:
        super().__init__(name, win_size)

    @count_exec_time
    def calculate(self, frame) -> tuple:
        """
        Calculate texture analysis metrics from the image's GLCM.

        Parameters:
        input_img (np.ndarray): The input image in grayscale.

        Returns:
        tuple: A tuple containing the GLCM texture metrics: contrast, homogeneity, energy, and correlation.
        """
        # Convert image pixels to the range [0, 15] for GLCM analysis
        input_img_quantized = (frame / 16).astype(np.uint8)

        # Compute GLCM
        glcm = greycomatrix(input_img_quantized, distances=[1], angles=[
                            0], levels=16, symmetric=True, normed=True)

        # Compute GLCM properties
        contrast = greycoprops(glcm, 'contrast')[0, 0]
        homogeneity = greycoprops(glcm, 'homogeneity')[0, 0]
        energy = greycoprops(glcm, 'energy')[0, 0]
        correlation = greycoprops(glcm, 'correlation')[0, 0]

        return { "contrast": contrast, "homogeneity": homogeneity, "energy": energy, "correlation" : correlation }
