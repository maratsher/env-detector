import time
import traceback

from datetime import datetime, timedelta

import cv2
from apscheduler.schedulers.background import BackgroundScheduler

from multiprocessing import Pipe
# from datetime import datetime

from env_detector.tuner import RequestManager, CameraTuner, MotorTuner, TelemetryTuner
from env_detector.controller import CameraControlАlgorithm, DayPreset, NightPreset
from env_detector.config import logger, APP_SETTINGS
from env_detector.utils import Commands
from env_detector.api import FlaskAPI
from env_detector.metrics import PixelMetric, DynamicRangeMetric, GLCMMetric, TextureMetric, BaseMetric, SSIMMetric, SharpnessMetric, RMSMetric
from env_detector.images_reader import ImageFlow


class Service:

    def __init__(self) -> None:
        # frame reader
        self._get_frame_sch = BackgroundScheduler()
        self._get_frame_sch.add_job(self._get_frame, 'interval', seconds=5)
        self._is_get_frame = False
        self._get_frame_sch.start()
        
        self._img_flow = ImageFlow("/tmp/storage/snap-pass")
        
        # logging    
        self._log_dir = "ed_logs"
        self._save_frame_sch = BackgroundScheduler()
        self._save_frame_sch.add_job(self._save_frame, "interval", seconds=60*60)
        self._is_save_frame = False
        self._save_frame_sch.start()

        # metrics
        # self._simple_metrics: list[BaseMetric] = [
        #     PixelMetric("Pixel Metric", 10), DynamicRangeMetric("Dynamic range"), GLCMMetric("GLCM"), TextureMetric("Texture"), 
        #     SharpnessMetric("Sharpness")]
        self._simple_metrics: list[BaseMetric] = [
            PixelMetric("Pixel Metric", 10)]
                
        # start the FlaskAPI process        
        self._cor_conn, self._api_conn = Pipe()
        self._flask_api = FlaskAPI(self._api_conn, port=APP_SETTINGS.PORT)
        self._flask_api.start()
        
        # service settings 
        self._fps = 0.1
        self._running = False
        
        # camera settings
        self._base_url = "http://10.135.2.15"    
 
        self._url_cam = f"{self._base_url}:8059"
        self._url_motor = f"{self._base_url}:8070"
        self._url_telemetry = f"{self._base_url}:8090"
        
        self._api_cam = RequestManager(self._url_cam)
        self._api_motor = RequestManager(self._url_motor)
        self._api_telemetry = RequestManager(self._url_telemetry)
        
        self._camera = CameraTuner(self._api_cam)
        self._motor = MotorTuner(self._api_motor)
        self._telemetry = TelemetryTuner(self._api_telemetry)
        
        self._camera_controller = CameraControlАlgorithm(camera=self._camera, motor=self._motor, 
                                                         telemetry=self._telemetry)
        
        # set started preset
        time_plus_three_hours = datetime.now() + timedelta(hours=3)
    
        morning_time = time_plus_three_hours.replace(hour=8, minute=0, second=0, microsecond=0)
        evening_time = time_plus_three_hours.replace(hour=19, minute=0, second=0, microsecond=0)
        
        if morning_time <= time_plus_three_hours < evening_time:
            logger.info("Setted Day mode[started]")
            DayPreset().apply(self._camera, self._motor, self._telemetry)
            self._camera_controller.mode = "Day"
        else:
            logger.info("Setted Night mode[started]")
            NightPreset().apply(self._camera, self._motor, self._telemetry)
            self._camera_controller.mode = "Night"
              
    def start(self):
        logger.info("Started servive...")
        self._running = True
        self._run()
        
    def _get_frame(self):
        self._is_get_frame = True
        
    def _save_frame(self):
        self._is_save_frame = True

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
                    
                    if frame is None:
                        continue 
                              
                    metrics_dic = {}
                    for metric in self._simple_metrics:
                        # calculate matrics
                        metrics_scores = metric.calculate(frame, bboxes)
                        # make pickle
                        metrics_dic[metric.name] = metrics_scores
                    # logging
                    logger.info(f"Metrics: {metrics_dic}")
                    
                    # save frame
                    if self._is_save_frame:
                        self._is_save_frame = False
                        dt = time.time() + timedelta(hours=3)
                        cv2.imwrite(f"{self._log_dir}/{dt}.jpg", frame)
                    
                # update cam settings
                self._camera_controller.update()
                
                # stop for a set time
                time.sleep(1/self._fps)

        except KeyboardInterrupt:
            logger.info("Keyboard Interrupt")
        except Exception as e:
            print(f"Error occurred: {e}\n{traceback.format_exc()}")
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
            
