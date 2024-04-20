# action/base_action.py
from abc import abstractmethod


class BaseAction:
    @abstractmethod
    def handle(self, parameters: dict):
        raise NotImplementedError("This method should be overridden by subclasses")
