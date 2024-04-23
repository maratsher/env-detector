class Preset:
    def __init__(self, settings):
        self.settings = settings

    def apply(self, camera_settings_manager):
        return camera_settings_manager.apply_settings(self.settings)

class DayPreset(Preset):
    def __init__(self):
        super().__init__({
            "GainAuto": "Continuous",
            "AutoTargetBrightness": 25,
            "AutoGainLowerLimit": 1.0,
            "AutoGainUpperLimit": 32.0,
            "Gamma": 0.8,
            "Brightness": 90,
            "Contrast": 51,
            "SetPulse": 1
        })

class NightPreset(Preset):
    def __init__(self):
        super().__init__({
            "GainAuto": "Continuous",
            "AutoTargetBrightness": 50,
            "AutoGainLowerLimit": 1.0,
            "AutoGainUpperLimit": 32.0,
            "Gamma": 0.6,
            "Brightness": 100,
            "Contrast": 45,
            "SetPulse": 100
        })