import abc


class BaseTuner(metaclass=abc.ABCMeta):

    def apply_settings(self, settings_dict):
        responses = {}
        for setting, value in settings_dict.items():
            response = self._set_setting(setting, value)
            responses[setting] = response
        return responses
    
    def get_settings(self, settings):
        return {name: self._get_setting(name, type) for name, type in settings}
    
    @abc.abstractmethod
    def _set_setting(self, setting_name, value):
        return None
    
    @abc.abstractmethod
    def _get_setting(self, name, type):
        return None