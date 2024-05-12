import time
import traceback

from datetime import datetime, timedelta

from multiprocessing import Pipe
# from datetime import datetime

from env_detector.tuner import RequestManager, CameraTuner, MotorTuner, TelemetryTuner
from env_detector.controller import CameraControlАlgorithm, DayPreset, NightPreset
from env_detector.config import logger, APP_SETTINGS
from env_detector.utils import Commands
from env_detector.api import FlaskAPI


class Service:

    def __init__(self) -> None:
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
    
        morning_time = time_plus_three_hours.replace(hour=8, minute=30, second=0, microsecond=0)
        evening_time = time_plus_three_hours.replace(hour=19, minute=30, second=0, microsecond=0)
        
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
            
