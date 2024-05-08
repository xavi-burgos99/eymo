# action/base_action.py
from abc import abstractmethod


class BaseAction:
    def __init__(self):
        pass

    def parameter_must_be_sent(self, parameter_name: str):
        return "Parameter '{}' must be sent".format(parameter_name)

    def response_json(self, action, result: str) -> dict:
        if result is None:
            status = "404 NOT FOUND"
        elif result == "":
            status = "204 NO CONTENT"
        else:
            status = "200 OK"
        
        return {
            'status': status,
            'action': action,
            'response': {
                'result': result,
            }
        }

    @abstractmethod
    def handle(self, parameters: dict):
        raise NotImplementedError("This method should be overridden by subclasses")