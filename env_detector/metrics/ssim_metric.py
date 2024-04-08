from env_detector.metrics import RelativeMetric

from skimage.metrics import structural_similarity as ssim


class SSIMMetric(RelativeMetric):

    def __init__(self) -> None:
        super().__init__()
        self._reference_frame = None

    def set_reference(self, reference):
        self._reference_frame = reference

    def calculate(self, frame) -> tuple:
        (score, _) = ssim(frame, self._reference_frame, full=True)

        return (score, )
