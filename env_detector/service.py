import time
import traceback

from datetime import datetime

import cv2
from apscheduler.schedulers.background import BackgroundScheduler

from multiprocessing import Value, Pipe
# from datetime import datetime

from env_detector.camera import TcpCamera, ImgCamera, API, CameraSettingsManager, MotorSettingsManager
from env_detector.controller import CameraControl
from env_detector.config import logger, APP_SETTINGS, SRC
from env_detector.utils import IMAGE_FORMAT, Commands
from env_detector.api import FlaskAPI
from env_detector.metrics import PixelMetric, DynamicRangeMetric, GLCMMetric, TextureMetric, BaseMetric, SSIMMetric, SharpnessMetric, RMSMetric
from env_detector.images_reader import ImageFlow


class Service:

    def __init__(self) -> None:
        # setting the source for receiving frames
        # self._cam_stop_flag = Value('i', 0)
        # if APP_SETTINGS.SOURCE == SRC.cam.value:
        #     self._camera = TcpCamera(is_stop=self._cam_stop_flag)
        # elif APP_SETTINGS.SOURCE == SRC.img.value:
        #     self._camera = ImgCamera(input="dataset/", repeat_times=1)
        self._scheduler = BackgroundScheduler()
        self._scheduler.add_job(self._get_frame, 'interval', seconds=10)
        self._is_get_frame = False
        self._scheduler.start()
        
        self._img_flow = ImageFlow("/home/npo/docker/storage/snap-pass")
            
        self._log_dir = "ed_logs"

        self._simple_metrics: list[BaseMetric] = [
            PixelMetric("Pixel Metric", 10), DynamicRangeMetric("Dynamic range"), GLCMMetric("GLCM"), TextureMetric("Texture"), 
            SharpnessMetric("Sharpness")]
        
        self._ssim = SSIMMetric("SSIM")
        
        # start the FlaskAPI process        
        self._cor_conn, self._api_conn = Pipe()
        self._flask_api = FlaskAPI(self._api_conn, port=APP_SETTINGS.PORT)
        self._flask_api.start()
                
        self._fps = 0.1
        self._running = False
        
        # camera settings
        self._base_url = "http://10.135.2.15"    
 
        self._url_cam = f"{self._base_url}:8059"
        self._url_motor = f"{self._base_url}:8070"
        
        self._api_cam = API(self._url_cam)
        self._api_motor = API(self._url_motor)
        
        self._csm = CameraSettingsManager(self._api_cam)
        self._msm = MotorSettingsManager(self._api_motor)
        
        self._camera_controller = CameraControl(self._csm, self._msm)
        

    def start(self):
        self._running = True
        self._run()
        
    def _get_frame(self):
        self._is_get_frame = True

    def _run(self):
        try:
            while True:
                # accept requests from flask api process
                if self._cor_conn.poll():
                    msg = self._cor_conn.recv()
                    self._message_handler(msg)
                    
                # skip if not running
                if not self._running:
                    time.sleep(1)
                    continue
                
                if self._is_get_frame:
                    self._is_get_frame = False
                    frame, bboxes = self._img_flow.get_frame()                
                    if frame: 
                        metrics_dic = {}
                        for metric in self._simple_metrics:
                            # calculate matrics
                            metrics_scores = metric.calculate(frame, bboxes)
                            # make pickle
                            metrics_dic[metric.name] = metrics_scores
                        # logging
                        logger.info(f"Metrics: {metrics_dic}")
                    
                    # update cam settings
                    self._camera_controller.update()
                    
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
            
