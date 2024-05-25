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

        self.auth_endpoint = config.get("auth").get("endpoint")
        self.auth_data = {
            'username': config.get("auth").get("username"),
            'password': config.get("auth").get("password"),
        }

        self.token = None
        self.__get_token__()

    def __get_token__(self):
        """
        Get the token from the server.
        :return: Token from the server.
        """
        logging.info("Getting token from the server...")
        response = requests.post(f"{self.host}/{self.auth_endpoint}",
                                 headers={
                                     'accept': 'application/json',
                                     'Content-Type': 'application/x-www-form-urlencoded'
                                 },
                                 data=self.auth_data,
                                 verify=False)
        if response.status_code == 200:
            self.token = response.json()['access_token']
        else:
            logging.error(f"Failed to get token from the server. Status code: {response.status_code}. Reason: {response.reason}")
            self.token = None

    def call_server(self, action: str, params: dict) -> str | Any:
        """
        Call the server with the given action and parameters.
        :param action: Action to be performed on the server.
        :param params: Parameters required for the action.
        :return: Response from the server.
        """
        if not self.token:
            self.__get_token__()

        serverIn = ServerIn()
        serverIn.action = action
        serverIn.parameters = params

        logging.info(f"Calling server {self.host}/{self.endpoint} with {serverIn.__dict__}...")
        for attempt in range(3):
            try:
                response = requests.get(f"{self.host}/{self.endpoint}",
                                        json=serverIn.__dict__,
                                        headers={
                                            'Content-Type': 'application/json',
                                            'Authorization': f'Bearer {self.token}'
                                        },
                                        verify=False)
                logging.info(f"Server response: {response}")
                if response.status_code == 200:
                    return response.json()
                else:
                    logging.error(
                        f"Failed to call server. Status code: {response.status_code}. Reason: {response.reason}")
                    if response.status_code == 401:
                        logging.info("Token might have expired, refreshing token...")
                        self.__get_token__()
                        if not self.token:
                            break
                    logging.info(f"Retrying... ({attempt + 1}/3)")
                    time.sleep(1)
            except RequestException:
                logging.error("Failed to connect to the server. Please check the server configurations.")
                logging.info(f"Retrying... ({attempt + 1}/3)")
                time.sleep(1)

        return "Ha habido un problema de conexion con el servidor. Por favor, intenta de nuevo."
