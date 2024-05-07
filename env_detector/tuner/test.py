from camera_tuner import CameraTuner
from motor_tuner import MotorTuner
from telemetry_tuner import TelemetryTuner
from request_manager import RequestManager

base_url = "http://10.135.2.15"    
 
url_camera = f"{base_url}:8059"
url_motor = f"{base_url}:8070"
url_telemetry = f"{base_url}:8090"

api_camera = RequestManager(url_camera)
api_motor = RequestManager(url_motor)
api_telemetry = RequestManager(url_telemetry)

camera_tuner = CameraTuner(api_camera)
motor_tuner = MotorTuner(api_motor)
telemetry_tuner = TelemetryTuner(api_telemetry)

class Preset:
    def __init__(self, settings):
        self.settings = settings

    def apply(self, camera, motor, telemetry):
        ans = camera.apply_settings(self.settings["camera"])
        print(ans)
        ans = motor.apply_settings(self.settings["motor"])
        print(ans)
        ans = telemetry.apply_settings(self.settings["telemetry"])
        print(ans)
        

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
            "AutoTargetBrightness": 60,
            "AutoGainLowerLimit": 1.0,
            "AutoGainUpperLimit": 32.0,
            "Gamma": 0.6,
            "Brightness": 100,
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
            "Pulse": 100  
        },
        "motor":
        {
            "ApertudeTo": 100
        }
        
        })
        
        
settings_to_apply = {}
current_settings = camera_tuner.get_settings([("ExposureTime", "float"), ("Gain", "float")])
exposure_time = current_settings['ExposureTime']["value"]
gain = current_settings['Gain']["value"]

aperture = int(motor_tuner.get_settings([("ApertudeAt", None)])["ApertudeAt"]["value"])


print(exposure_time)
print(gain)
print(aperture)



