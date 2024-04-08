import time
import traceback
import pickle

from datetime import datetime

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
            
        self._log_dir = "ed_logs/"

        self._simple_metrics: list[BaseMetric] = [
            AverageMetric("Average brightness"), DynamicRangeMetric("Dynamic range"), GLCMMetric("GLCM"), TextureMetric("Texture")]

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
                    dt = datetime.fromtimestamp(frame_data.metadata.timestamp)
                    
                    if frame_data:
                        # convert bayer to greyscale if necessary
                        if frame_data.pixel_format == IMAGE_FORMAT.BAYERRG8:
                            self._curr_frame = cv2.cvtColor(
                                frame_data.frame, cv2.COLOR_BayerRG2RGB)
                            self._curr_frame = cv2.cvtColor(
                                self._curr_frame, cv2.COLOR_RGB2GRAY)
                        else:
                            self._curr_frame = frame_data.frame

                        metrics_dic = {}
                       
                        for metric in self._simple_metrics:
                            # calculate matrics
                            metrics_scores = metric.calculate(self._curr_frame)
                            
                            # save txt
                            with open(f"{self._log_dir}{dt}.txt", "a") as file:
                                file.write(metric._name+"\n")
                                for name, score in metrics_scores.items():
                                    file.write(f"{name} = {score}; ")
                                file.write("\n\n")
                                
                                #TODO remove
                                #print(f"{metric.name} : {metric.calculate(self._curr_frame)} : {metric.exec_time}")
                                
                            # make pickle
                            metrics_dic[metric._name] = metrics_scores
                        
                        # save pickle    
                        with open(f'{self._log_dir}{dt}.pickle', 'wb') as f:
                            pickle.dump(metrics_dic, f)
                                
                        # save image
                        cv2.imwrite(f"{self._log_dir}/{dt}.png", self._curr_frame)
                        
                        # stop for a set time
                        time.sleep(1)
                    else:
                        logger.debug("Failed to capture the frame")
        except KeyboardInterrupt:
            logger.info("Keyboard Interrupt")
            self._camera._exit()
        except Exception as e:
            print(f"Error occurred: {e}\n{traceback.format_exc()}")
            self._camera._exit()
        finally:
            logger.info("Service stopped...")
