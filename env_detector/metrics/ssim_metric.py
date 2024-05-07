from env_detector.metrics import RelativeMetric, count_exec_time

# from skimage.metrics import structural_similarity as ssim


class SSIMMetric(RelativeMetric):
    
    pass

    # def __init__(self, name, win_size=0) -> None:
    #     super().__init__(name, win_size)
    #     self._reference_frame = None

    # def set_reference(self, reference):
    #     self._reference_frame = reference

    # @count_exec_time
    # def calculate(self, frame, bboxes=None) -> tuple:
    #     if self._reference_frame is None:
    #         return { "ssim_score": None }
        
    #     (score, _) = ssim(frame, self._reference_frame, full=True)
    #     return { "ssim_score": score,  }
