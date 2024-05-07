import requests

class API:
    def __init__(self, base_url):
        self.base_url = base_url

    def get(self, endpoint):
        response = requests.get(f"{self.base_url}{endpoint}")
        return response.json()

    def post(self, endpoint, data):
        response = requests.post(f"{self.base_url}{endpoint}", json=data)
        return response.json()

class MotorSettingsManager:
    def __init__(self, api):
        self.api = api

    def get_value(self, param):
        
        endpoint = f'/v1/{param}'
        return self.api.get(endpoint)
    
base_url = "http://10.135.2.15"    
 
url_motor = f"{base_url}:8070"

api_motor = API(url_motor)

motor_settrings_manager = MotorSettingsManager(api_motor)

response = motor_settrings_manager.apply_command("diaphragm")
print(response["value"])
print(int(response["value"]))