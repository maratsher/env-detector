from env_detector.tuner import BaseTuner

class MotorTuner(BaseTuner):
    def __init__(self, api):
        self.api = api

    def _set_setting(self, setting_name, value):
        endpoint = ""
        if setting_name == "ApertudeAt":
            endpoint = '/v1/diaphragm/move-at'
        elif setting_name == "ApertudeTo":
            endpoint = '/v1/diaphragm/move-to'
        else: 
            return None
        return self.api.post(endpoint, {"value": value})
    
    def _get_setting(self, name, type):
        endpoint = ""
        if name == "ApertudeAt":
            endpoint = '/v1/diaphragm'
        elif name == "ApertudeTo":
            endpoint = '/v1/diaphragm'
        else:
            return None
        return self.api.get(endpoint)
    
    