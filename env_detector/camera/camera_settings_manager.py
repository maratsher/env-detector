class CameraSettingsManager:
    def __init__(self, api):
        self.api = api

    def set_setting(self, setting_name, value):
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

    def apply_settings(self, settings_dict):
        responses = {}
        for setting, value in settings_dict.items():
            response = self.set_setting(setting, value)
            responses[setting] = response
        return responses

    def get_setting(self, setting_name):
        # Guessing type from name as we can't determine the exact type from this function
        data_type = "int" if "int" in setting_name.lower() else "float" if "float" in setting_name.lower() else "string"
        endpoint = f'/v1/camera/get-{data_type}-value'
        return self.api.post(endpoint, {"name": setting_name})

    def get_settings(self, setting_names):
        return {name: self.get_setting(name) for name in setting_names}