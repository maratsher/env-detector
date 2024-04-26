from env_detector.controller import DayPreset, NightPreset
from env_detector.config import logger

class CameraControl:
    def __init__(self, camera_settings_manager, motor_settings_manager):
        self._cms = camera_settings_manager
        self._msm = motor_settings_manager
        
        self.mode = 'Day'  # Default mode is Day
        self.presets = {
            'Day': DayPreset(),
            'Night': NightPreset()
        }
        
        logger.info("Init camera control")

    def update(self):
        settings_to_apply = {}
        current_settings = self._cms.get_settings([("ExposureTime", "float"), ("Gain", "float")])
        exposure_time = current_settings['ExposureTime']["value"]
        gain = current_settings['Gain']["value"]
        aperture = int(self._msm.apply_command("diaphragm", "move-at", 0)["value"])
        
        logger.info(f"INPUT: ExposureTime {exposure_time} Gain {gain} Aperture {aperture}")

        if self.mode == 'Day':
            if gain > 3.5:
                if exposure_time < 3000:
                    settings_to_apply["ExposureTime"] = float(exposure_time + 10)
                elif gain >= 15:
                    if aperture < 100:
                        #settings_to_apply["Aperture"] = aperture + 10
                        self._msm.apply_command("diaphragm", "move-at", 10)
                    if gain >= 30:
                        self.switch_mode('Night')
            elif gain <= 1.5:
                if exposure_time > 300:
                    settings_to_apply["ExposureTime"] = float(exposure_time - 10)
                if aperture > 40:
                    #settings_to_apply["Aperture"] = aperture - 0.1
                    self._msm.apply_command("diaphragm", "move-at", -10)

        elif self.mode == 'Night':
            if gain <= 20:
                if aperture > 50:
                    #settings_to_apply["Aperture"] = aperture - 0.1
                    self._msm.apply_command("diaphragm", "move-at", -10)
                elif gain < 1.5:
                    if exposure_time > 500:
                        settings_to_apply["ExposureTime"] = float(exposure_time - 10)
                    else:
                        self.switch_mode('Day')
        
        logger.info(f"SETTED: {settings_to_apply}")
        self._cms.apply_settings(settings_to_apply)

    def switch_mode(self, mode):
        logger.info(f"Switched mode to {mode}")
        self.mode = mode
        self.presets[mode].apply(self.manager)