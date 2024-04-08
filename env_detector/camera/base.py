import abc


class BaseCamera(metaclass=abc.ABCMeta):

    def __enter__(self, *args, **kwargs):
        self._init()
        return self

    def __exit__(self, *exc):
        return self._exit()

    @abc.abstractmethod
    def _init(self):
        pass

    @abc.abstractmethod
    def _exit(self):
        pass

    def _reconnect(self):
        self._exit()
        self._init()

    @abc.abstractmethod
    def get_image(self):
        return None

    @abc.abstractmethod
    def get_probe(self):
        return {}
