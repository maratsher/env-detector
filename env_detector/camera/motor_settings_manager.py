class MotorSettingsManager:
    def __init__(self, api):
        self.api = api

    def apply_command(self, param, command, value):
        
        endpoint = f'/v1/{param}/{command}'
        return self.api.post(endpoint, {"value": value})