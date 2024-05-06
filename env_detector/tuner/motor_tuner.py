from base_tuner import BaseTuner

class MotorTuner(BaseTuner):
    def __init__(self, api):
        self.api = api

    def _set_setting(self, setting_name, value):
        if setting_name == "ApertudeAt":
            endpoint = '/v1/diaphragm/move-at'
        elif setting_name == "ApertudeTo":
            endpoint = '/v1/diaphragm/move-to'
        return self.api.post(endpoint, {"value": value})
    
    def _get_setting(self, name, type):
        if name == "ApertudeAt":
            endpoint = '/v1/diaphragm'
        elif name == "ApertudeTo":
            endpoint = '/v1/diaphragm'
        return self.api.get(endpoint)
    
    