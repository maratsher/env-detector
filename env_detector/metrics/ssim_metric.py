from env_detector.metrics import RelativeMetric, count_exec_time

from skimage.metrics import structural_similarity as ssim


class SSIMMetric(RelativeMetric):

    def __init__(self, name) -> None:
        super().__init__(name)
        self._reference_frame = None

    def set_reference(self, reference):
        self._reference_frame = reference

    @count_exec_time
    def calculate(self, frame) -> tuple:
        (score, _) = ssim(frame, self._reference_frame, full=True)

        return { "ssim_score", score }
