from contextlib import ContextDecorator
from typing import Optional
from pathlib import Path

import cv2

from env_detector.utils.camera_utils import ImageFrame, FrameMetadata, IMAGE_FORMAT
from env_detector.camera.base import BaseCamera

from env_detector.config import logger


class ImgCamera(ContextDecorator, BaseCamera):
    def __init__(self, input: str, repeat_times: int, **kvargs):
        """
        Чтение кадров видео через opencv
        видео на диске:
            input = абсолютный путь к файлу видео
            retries не используется
        rtsp:
            input = абсолютный путь к файлу видео
            retries > 0 = число попыток реконнекта
        """
        self.input = Path(input)
        self.repeat_time = repeat_times
        self._frame_count = -1
        self._current_frame_number = -1
        self.gen_frames = self.frame_stream_gen()
        self._frames = []


        try:
            from turbojpeg import TurboJPEG, TJPF_GRAY
            self._jpeg_method = 'TurboJPEG'
        except:
            logger.info('\n\n TurboJPEG library is not avaible. To use, please install https://pypi.org/project/PyTurboJPEG/ \n\n')
            self._jpeg_method = 'cv2'
        self.jpeg_reader = None if self._jpeg_method == 'cv2' else TurboJPEG()
    
    def prepare_links(self):
        if not self.input.is_dir():
            return False
        
        inp = self.input / 'imgs' if (self.input / 'imgs').is_dir() else self.input
        jpg = list(inp.glob("*.jpg"))
        png = list(inp.glob("*.png"))
        imgs = jpg if len(jpg) > len(png) else png
        for l in imgs:
            try:
                _ = int(l.stem)
                self._frames.append(l)
            except Exception:
                pass
        self.delta = int(self._frames[-1].stem) - int(self._frames[0].stem) + int(self._frames[1].stem) - int(self._frames[0].stem)
        self._frames.sort(key=lambda x: x.stem)
        # print(f"Load {len(self._frames)} from {str(inp)}")

    def frame_stream_gen(self):
        for r in range(self.repeat_time):
            for i, img in enumerate(self._frames):
                try:
                    if self._jpeg_method == 'cv2' or img.suffix != '.jpg':
                        yield cv2.imread(str(img), cv2.IMREAD_GRAYSCALE), int(img.stem) + r * self.delta
                    else:
                        with open(str(img), "rb") as file:
                            jpg_buff = file.read()
                            yield self.jpeg_reader.decode(jpg_buff, pixel_format=TJPF_GRAY),  int(img.stem) + r * self.delta
                except Exception as e:
                    pass
        raise StopIteration

    def _init(self):
        logger.info(f"Start cam from {self.__class__.__name__} source")
        self.prepare_links()

    @property
    def shape(self):
        return (2448, 2048,)

    def _exit(self):
        logger.info("Exit ImgCam")

    def get_image(self) -> Optional[ImageFrame]:
        """Get frame with timestamp or reconnect.

        :return: frame with timestamp metadata 
        :rtype: Tuple[Optional[np.array], Optional[float]]
        """
        try:
            (img, ts) = next(self.gen_frames)
            t = FrameMetadata(ts / 1000, 0, 0)
        except Exception as e:
            return None
        except KeyboardInterrupt:
            return None
        return ImageFrame(img.squeeze(), t, IMAGE_FORMAT.GRAY)

    # :TODO remove hardcode
    def get_probe(self):
        return {
            "width": 2448,
            "height": 2048,
            "frames_per_second": 20
        }
