import multiprocessing as mp
import numpy as np
from typing import Generator
import enum

class IMAGE_FORMAT(enum.IntEnum):
    GRAY = 0
    BAYERRG8 = 1


class FrameMetadata:
    def __init__(self, timestamp, gain, exposure):
        """
        timestamp: unixtime in second
        """
        self.timestamp = timestamp
        self.gain = gain
        self.exposure = exposure


class ImageFrame:

    def __init__(self, frame: np.ndarray, metadata: FrameMetadata, pixel_format: IMAGE_FORMAT):
        self.frame = frame
        self.metadata = metadata
        self.pixel_format = pixel_format


class CameraError(Exception):
    """
    Exception for incorrect use of cameras
    """

    pass


def frames_generator(
    camera,
    batch_size=10,
) -> Generator[list, None, None]:
    """Generate frames batch.

    yields np.array with shape (batch_size, height, width, 1)
    """
    if batch_size == 1:
        while True:
            img = camera.get_image()
            if img is not None:
                yield [img]
            else:
                break
    else:
        batch = []
        while True:
            try:
                img = camera.get_image()
                if img is not None:
                    batch.append(img)
                else:
                    break
            finally:
                if len(batch) == batch_size:
                    yield batch  # NOTE: Keep as list for not to lose metadata
                    for i in reversed(range(len(batch))):
                        batch[i] = None
                        del batch[i]


class LockQueue:
    def __init__(self, qeue_len) -> None:
        self.qeue_len = qeue_len
        self.semafore = mp.Semaphore(qeue_len)
        self.queue_ptr = mp.Value('i', -1)

    def acquire(self):
        self.semafore.acquire()
        self.queue_ptr.value = self.queue_ptr.value + 1
        if self.queue_ptr.value >= self.qeue_len:
            self.queue_ptr.value = 0

        return self.queue_ptr.value

    def release(self):
        self.semafore.release()
