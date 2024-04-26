# from env_detector import Service

# env_detector_service = Service()
# env_detector_service.start()


# # testing
# from env_detector.camera import API, CameraSettingsManager, MotorSettingsManager
# base_url = "http://192.168.64.77"    
 
# url_cam = f"{base_url}:8059"
# url_motor = f"{base_url}:8059"

# api_cam = API(url_cam)
# api_motor = API(url_motor)

# camera_settings_manager = CameraSettingsManager(api_cam)
# motor_settrings_manager = MotorSettingsManager(api_motor)

# # Пример настройки параметров камеры
# settings_to_apply = {
#     "ExposureTime": 800.0,
#     "Gain": 5.0,
# }
# response = camera_settings_manager.apply_settings(settings_to_apply)
# print(response)

# # Пример получения значений настроек
# settings_to_retrieve = [("ExposureTime", "float"), ("Gain", "float"), ("Gamma", "float")]
# settings_values = camera_settings_manager.get_settings(settings_to_retrieve)
# print(settings_values)


# # Двигаем диофграму 
# response = motor_settrings_manager.apply_command("diaphragm", "move-at", 0)
# print(response)



