from env_detector.tuner import BaseTuner

class TelemetryTuner(BaseTuner):
    def __init__(self, api):
        self.api = api

    def _set_setting(self, setting_name, value):
        if setting_name == "Pulse":
            endpoint = '/p/'
        return self.api.post(endpoint, {"value": value})
    
    def _get_setting(self, name, type):
        if name == "Pulse":
            endpoint = '/p/'
        return self.api.get(endpoint)
    