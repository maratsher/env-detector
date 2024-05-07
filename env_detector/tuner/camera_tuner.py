from env_detector.tuner import BaseTuner

class CameraTuner(BaseTuner):
    
    def __init__(self, api):
        self.api = api

    def _set_setting(self, setting_name, value):
        data_type = type(value)
        if data_type == int:
            endpoint = '/v1/camera/set-int-value'
        elif data_type == float:
            endpoint = '/v1/camera/set-float-value'
        elif data_type == str:
            endpoint = '/v1/camera/set-string-value'
        else:
            raise ValueError("Unsupported data type for camera setting")

        return self.api.post(endpoint, {"name": setting_name, "value": value})

    def _get_setting(self, name, type):
        endpoint = f'/v1/camera/get-{type}-value'
        return self.api.post(endpoint, {"name": name})