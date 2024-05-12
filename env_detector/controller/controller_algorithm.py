from env_detector.controller import DayPreset, NightPreset
from env_detector.tuner import CameraTuner, MotorTuner, TelemetryTuner 
from env_detector.config import logger

class CameraControlАlgorithm:
    def __init__(self, camera, motor, telemetry):
        self._camera: CameraTuner = camera
        self._motor: MotorTuner = motor
        self._telemetry: TelemetryTuner = telemetry 
        
        self.mode = 'Day'  # Default mode is Day
        self.presets = {
            'Day': DayPreset(),
            'Night': NightPreset()
        }
        
        logger.info("Init camera control")

    def update(self):
        logger.info(f"Current mode: {self.mode}")
        settings_to_apply = {}
        current_settings = self._camera.get_settings([("ExposureTime", "float"), ("Gain", "float"), ("AutoTargetBrightness", "int")])
        exposure_time = current_settings['ExposureTime']["value"]
        gain = current_settings['Gain']["value"]
        at = current_settings['AutoTargetBrightness']["value"]
        
        try:
            aperture = int(self._motor.get_settings([("ApertudeAt", None)])["ApertudeAt"]["value"])
            pulse = int(self._telemetry.get_settings([("Pulse", None)])["Pulse"]["value"])
        except Exception as e:
            logger.info(f"in get {e}")
            return
        
        logger.info(f"INPUT: ExposureTime {exposure_time} Gain {gain} Aperture {aperture}")

        if self.mode == 'Day':
            if gain > 3.5:
                if exposure_time < 3000:
                    settings_to_apply["ExposureTime"] = float(exposure_time + 10)
                elif gain >= 8:
                    if at != 40:
                        settings_to_apply["AutoTargetBrightness"] = 40
                    if aperture < 91:
                        self._motor.apply_settings({"ApertudeAt": 10})
                    if gain >= 20:
                        if pulse != 50:
                            self._telemetry.apply_settings({"Pulse": 50})
                    if gain >= 30:
                        self.switch_mode('Night')
            elif gain <= 1.5:
                if exposure_time > 400:
                    settings_to_apply["ExposureTime"] = float(exposure_time - 10)
                if aperture >= 40 and aperture != 0:
                    self._motor.apply_settings({"ApertudeAt" : -10})
                if exposure_time <= 400:
                    if gain == 1.0:
                        if at != 25:
                            settings_to_apply["AutoTargetBrightness"] = 25
                        else:                      
                            if exposure_time > 200:
                                settings_to_apply["ExposureTime"] = float(exposure_time - 10)
            else:
                if at != 30 and exposure_time < 200:
                    settings_to_apply["AutoTargetBrightness"] = 30

        elif self.mode == 'Night':
            if gain <= 20:
                if aperture >= 50 and aperture < 91:
                    self._motor.apply_settings({"ApertudeAt" : 10})
                elif gain < 1.5:
                    if exposure_time > 500:
                        settings_to_apply["ExposureTime"] = float(exposure_time - 10)
                    else:
                        self.switch_mode('Day')
                        
            if gain <= 10:
                if pulse != 50:
                    self._telemetry.apply_settings({"Pulse": 50})
                    
            if gain >= 20:
                if pulse != 80:
                    self._telemetry.apply_settings({"Pulse": 80})
                
                        
        
        logger.info(f"SETTED: {settings_to_apply}")
        self._camera.apply_settings(settings_to_apply)

    def switch_mode(self, mode):
        logger.info(f"Switched mode to {mode}")
        self.mode = mode
        self.presets[mode].apply(self._camera, self._motor, self._telemetry)