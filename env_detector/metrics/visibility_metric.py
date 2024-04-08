import cv2

from env_detector.metrics import RelativeMetric


class VisibilityMetric(RelativeMetric):

    def __init__(self) -> None:
        super().__init__()
        self._composite_frame = None
        self._compasite_edges = None

        self._th1 = 100
        self._th2 = 200

    def set_reference(self, reference):
        self._composite_frame = reference
        self._compasite_edges = self._calculate_edges(reference)

    def _calculate_edges(self, frame):
        grad_x = cv2.Sobel(frame, cv2.CV_64F, 1, 0, ksize=3)
        grad_y = cv2.Sobel(frame, cv2.CV_64F, 0, 1, ksize=3)

        edges = grad_x + grad_y

        return edges

    def calculate(self, frame) -> tuple:

        self._current_edges = self._calculate_edges(frame)

        return None
