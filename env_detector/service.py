import time
import traceback

import cv2

from multiprocessing import Value
# from datetime import datetime

from env_detector.camera import TcpCamera, ImgCamera
from env_detector.config import logger, APP_SETTINGS, SRC
from env_detector.utils import IMAGE_FORMAT
from env_detector.metrics import AverageMetric, DynamicRangeMetric, GLCMMetric, TextureMetric, BaseMetric


class Service:

    def __init__(self) -> None:
        # setting the source for receiving frames
        self._cam_stop_flag = Value('i', 0)
        if APP_SETTINGS.SOURCE == SRC.cam.value:
            self._camera = TcpCamera(is_stop=self._cam_stop_flag)
        elif APP_SETTINGS.SOURCE == SRC.img.value:
            self._camera = ImgCamera(input="dataset_bad/", repeat_times=100)

        self._simple_metrics: list[BaseMetric] = [
            AverageMetric(), DynamicRangeMetric(), GLCMMetric(), TextureMetric()]

        self._running = False

    def start(self):
        self._running = True
        self._run()

    def _run(self):
        try:
            with self._camera:
                while True:
                    # skip if not running
                    if not self._running:
                        time.sleep(1)
                        continue

                    # get image from camera
                    frame_data = self._camera.get_image()

                    if frame_data:
                        # convert bayer to greyscale if necessary
                        if frame_data.pixel_format == IMAGE_FORMAT.BAYERRG8:
                            self._curr_frame = cv2.cvtColor(
                                frame_data.frame, cv2.COLOR_BayerRG2RGB)
                            self._curr_frame = cv2.cvtColor(
                                self._curr_frame, cv2.COLOR_RGB2GRAY)
                        else:
                            self._curr_frame = frame_data.frame

                        # calculate matrics
                        for metric in self._simple_metrics:
                            print(
                                f"{metric._name} : {metric.calculate(self._curr_frame)}")

                        # stop for a set time
                        time.sleep(self._grab_frame_interval/1000)
                    else:
                        logger.debug("Failed to capture the frame")
        except KeyboardInterrupt:
            logger.info("Keyboard Interrupt")
            self._camera._exit()
        except Exception as e:
            logger.info(f"Error occurred: {e}\n{traceback.format_exc()}")
            self._camera._exit()
        finally:
            logger.info("Service stopped...")
