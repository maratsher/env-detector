import abc

from env_detector.metrics import BaseMetric


class RelativeMetric(BaseMetric, metaclass=abc.ABCMeta):

    @abc.abstractmethod
    def set_reference(self, reference):
        pass
