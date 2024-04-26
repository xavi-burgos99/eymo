# action/base_action.py
from abc import abstractmethod


class BaseAction:
    def __init__(self):
        pass

    def parameter_must_be_sent(self, parameter_name: str):
        return "Parameter '{}' must be sent".format(parameter_name)

    @abstractmethod
    def handle(self, parameters: dict):
        raise NotImplementedError("This method should be overridden by subclasses")
