import time
from typing import Any

import requests
import logging

from requests import RequestException

from services.models.server_input import ServerIn


class ServerCommunication:
    def __init__(self, config: dict):
        self.host = config['host']
        self.endpoint = config['endpoint']

    def call_server(self, action: str, params: dict) -> str | Any:
        """
        Call the server with the given action and parameters.
        :param action: Action to be performed on the server.
        :param params: Parameters required for the action.
        :return: Response from the server.
        """
        serverIn = ServerIn()
        serverIn.action = action
        serverIn.parameters = params

        logging.info(f"Calling server {self.host}/{self.endpoint} with {serverIn.__dict__}...")
        for attempt in range(3):
            response = None
            try:
                response = requests.get(f"{self.host}/{self.endpoint}",
                                        json=serverIn.__dict__,
                                        headers={'Content-Type': 'application/json'},
                                        verify=False)
            except RequestException:
                logging.error("Failed to connect to the server. Please check the server configurations.")

            logging.info(f"Server response: {response}")
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Failed to call server. Status code: {response.status_code}. Reason: {response.reason}")
                logging.info(f"Retrying... ({attempt + 1}/{3})")
                time.sleep(1)

        return "Ha habido un problema de conexion con el servidor. Por favor, intenta de nuevo."
