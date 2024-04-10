import time
import traceback
import pickle

from datetime import datetime

import cv2
import os

from multiprocessing import Value, Pipe
# from datetime import datetime

from env_detector.camera import TcpCamera, ImgCamera
from env_detector.config import logger, APP_SETTINGS, SRC
from env_detector.utils import IMAGE_FORMAT, Commands, save_txt
from env_detector.api import FlaskAPI
from env_detector.metrics import PixelMetric, DynamicRangeMetric, GLCMMetric, TextureMetric, BaseMetric, SSIMMetric, SharpnessMetric, RMSMetric


class Service:

    def __init__(self) -> None:
        # setting the source for receiving frames
        self._cam_stop_flag = Value('i', 0)
        if APP_SETTINGS.SOURCE == SRC.cam.value:
            self._camera = TcpCamera(is_stop=self._cam_stop_flag)
        elif APP_SETTINGS.SOURCE == SRC.img.value:
            self._camera = ImgCamera(input="dataset/", repeat_times=1)
            
        self._log_dir = "ed_logs"

        self._simple_metrics: list[BaseMetric] = [
            PixelMetric("Pixel Metric", 10), DynamicRangeMetric("Dynamic range"), GLCMMetric("GLCM"), TextureMetric("Texture"), 
            SharpnessMetric("Sharpness"), RMSMetric("RMS")]
        
        self._ssim = SSIMMetric("SSIM")
        
        # start the FlaskAPI process        
        self._cor_conn, self._api_conn = Pipe()
        self._flask_api = FlaskAPI(self._api_conn, port=APP_SETTINGS.PORT)
        self._flask_api.start()
                
        self._fps = 0.1
        self._running = False

    def start(self):
        self._running = True
        self._run()

    def _run(self):
        try:
            with self._camera:
                while True:
                    
                    # accept requests from flask api process
                    if self._cor_conn.poll():
                        msg = self._cor_conn.recv()
                        self._message_handler(msg)
                        
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
                          
                        # make subdir 
                        subdir_path = f"{self._log_dir}/{dt}"
                        if not os.path.exists(subdir_path):
                            os.makedirs(subdir_path)

                        metrics_dic = {}
                       
                        for metric in self._simple_metrics:
                            # calculate matrics
                            metrics_scores = metric.calculate(self._curr_frame)
                            
                            # save txt
                            with open(f"{subdir_path}/{dt}.txt", "a") as file:
                                save_txt(file, metric.name, metrics_scores, metric.exec_time)
                                
                            # make pickle
                            metrics_dic[metric.name] = metrics_scores
                        
                        # save ssim
                        ssim_scores = self._ssim.calculate(self._curr_frame)
                        with open(f"{subdir_path}/{dt}.txt", "a") as file:
                            save_txt(file, self._ssim.name, ssim_scores, metric.exec_time)
                        metrics_dic[self._ssim.name] = ssim_scores
                            
                        # logging
                        logger.info(f"{dt}: {metrics_dic}")
                        
                        # save pickle    
                        with open(f'{subdir_path}/{dt}.pickle', 'wb') as f:
                            pickle.dump(metrics_dic, f)
                                
                        # save image
                        cv2.imwrite(f"{subdir_path}/{dt}.png", self._curr_frame)
                        
                        # stop for a set time
                        time.sleep(1/self._fps)
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
            
    def _message_handler(self, msg):
        command = msg["cmd"]
        args = msg["args"]
        
        if command == Commands.START:
            self._running = True
        elif command == Commands.STOP:
            self._running = False
        elif command == Commands.SET_FPS:
            self._fps = float(args)
        elif command == Commands.GET_FPS:
            self._cor_conn.send({"cmd": Commands.GET_FPS, "args": self._fps})
        elif command == Commands.SET_REF_SSIM:
            self._ssim.set_reference(self._curr_frame)
            logger.info("Setted new referance frame ssim")
