class Preset:
    def __init__(self, settings):
        self.settings = settings

    def apply(self, camera, motor, telemetry):
        camera.apply_settings(self.settings["camera"])
        
        # TODO change with MoveTo
        apertude_to = self.settings["motor"]["ApertudeTo"]
        apertude_cuurent = int(motor.get_settings([("ApertudeAt", None)])["ApertudeAt"]["value"])       
        apertude_at = apertude_to - apertude_cuurent
        motor.apply_settings({"ApertudeAt" : apertude_at})
        #motor.apply_settings(self.settings["motor"])    
        
        telemetry.apply_settings(self.settings["telemetry"])

class DayPreset(Preset):
    def __init__(self):
        super().__init__({
            "camera":
            {
                "GainAuto": "Continuous",
                "AutoTargetBrightness": 30,
                "AutoGainLowerLimit": 1.0,
                "AutoGainUpperLimit": 32.0,
                "Gamma": 0.8, # float
                "Brightness": 90, # int
                "Contrast": 51, # int
                "ContrastThreshold": 128,
                "FFCEnable": "On",
                "BlackLevel": 60,
                "SharpnessEnabled": "Off",
                "Sharpness": 50,
                "DenoisingEnabled": "Off",
                "Denoising": 50,
            }, 
            "telemetry":    
            {
                "Pulse": 1  
            },
            "motor":
            {
                "ApertudeTo": 10
            }
        })

class NightPreset(Preset):
    def __init__(self):
        super().__init__({
        "camera":
        {    
            "GainAuto": "Continuous",
            "AutoTargetBrightness": 50,
            "AutoGainLowerLimit": 1.0,
            "AutoGainUpperLimit": 32.0,
            "Gamma": 0.6,
            "Brightness": 80,
            "Contrast": 45,
            "ContrastThreshold": 20,
            "FFCEnable": "On",
            "BlackLevel": 60,
            "SharpnessEnabled": "Off",
            "Sharpness": 50,
            "DenoisingEnabled": "Off",
            "Denoising": 50,
        },
        "telemetry":    
        {
            "Pulse": 30  
        },
        "motor":
        {
            "ApertudeTo": 100
        }
        
        })