import requests
import logging

from src.rpi.services.models.server_input import ServerIn


class ServerCommunication:
    def __init__(self, config: dict):
        self.host = config['host']
        self.endpoint = config['endpoint']

    def call_server(self, action: str, params: dict) -> dict:
        """
        Call the server with the given action and parameters.
        :param action: Action to be performed on the server.
        :param params: Parameters required for the action.
        :return: Response from the server.
        """
        serverIn = ServerIn()
        serverIn.action = action
        serverIn.params = params

        logging.info(f"Calling server {self.host}/{self.endpoint} with action: {action}, params: {params}")
        response = requests.get(f"{self.host}/{self.endpoint}", json=serverIn.__dict__)
        logging.info(f"Server response: {response}")

        return response.json()
