from env_detector.controller import DayPreset, NightPreset

class CameraControl:
    def __init__(self, camera_settings_manager):
        self.manager = camera_settings_manager
        self.mode = 'Day'  # Default mode is Day
        self.presets = {
            'Day': DayPreset(),
            'Night': NightPreset()
        }

    def update(self, gain):
        settings_to_apply = {}
        current_settings = self.manager.get_settings(["ExposureTime", ""])
        exposure_time = current_settings['ExposureTime']
        aperture = current_settings['Aperture']

        if self.mode == 'Day':
            if gain > 3.5:
                if exposure_time < 3000:
                    settings_to_apply["ExposureTime"] = exposure_time + 1
                elif gain >= 15:
                    if aperture < 1.0:  # Assuming aperture is normalized from 0 to 1 for 100%
                        settings_to_apply["Aperture"] = aperture + 0.1
                    if gain >= 30:
                        self.switch_mode('Night')
            elif gain <= 1.5:
                if exposure_time > 300:
                    settings_to_apply["ExposureTime"] = exposure_time - 1
                if aperture > 0.4:
                    settings_to_apply["Aperture"] = aperture - 0.1

        elif self.mode == 'Night':
            if gain <= 20:
                if aperture > 0.5:
                    settings_to_apply["Aperture"] = aperture - 0.1
                elif gain < 1.5:
                    if exposure_time > 500:
                        settings_to_apply["ExposureTime"] = exposure_time - 1
                    else:
                        self.switch_mode('Day')

        self.manager.apply_settings(settings_to_apply)

    def switch_mode(self, mode):
        self.mode = mode
        self.presets[mode].apply(self.manager)