from abc import ABC

from src.cloud.actions.BaseAction import BaseAction


class TestAction(BaseAction, ABC):
    def handle(self, parameters: dict):
        return parameters
