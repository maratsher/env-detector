import cv2
import numpy as np

class ImageProcessor:
    def __init__(self, image_path):
        self._image_path = image_path
        self._width = 2448
        self._height = 2048

    def load_img(self):
        with open(self._image_path, 'rb') as file:
            buff = file.read()
            img_array = np.frombuffer(buff, dtype=np.uint8).reshape((self._height, self._width))

        frame = cv2.cvtColor(img_array, cv2.COLOR_BayerRG2GRAY)
        return frame
    
