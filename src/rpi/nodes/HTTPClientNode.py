import rclpy
import requests
import json

from rclpy.node import Node
from requests import HTTPError, ConnectionError, Timeout, RequestException
from ..services import SendHttpRequest

URL = 'http://localhost:7125/'  # Change URL accordingly
TOKEN = "Put your token here"


class HTTPClientNode(Node):
    def __init__(self):
        super().__init__('http_client_node')
        self.srv = self.create_service(SendHttpRequest, 'send_http_request', self.handle_http_request)

    def handle_http_request(self, parameters: dict, response: requests.Response):
        try:
            headers = {
                'Authorization': 'Bearer {token}'.format(token=TOKEN),
                'Content-Type': 'application/json'
            }
            response_data = requests.get(URL, headers=headers, data=parameters)
            response_data.raise_for_status()
            response.response = response_data.text
            response.success = True
        except HTTPError as errh:
            response.success = False
            response.error_message = str(errh)
        except ConnectionError as errc:
            response.success = False
            response.error_message = str(errc)
        except Timeout as errt:
            response.success = False
            response.error_message = str(errt)
        except RequestException as err:
            response.success = False
            response.error_message = "An unexpected error occurred: " + str(err)
        return response


def main(args=None):
    rclpy.init(args=args)
    node = HTTPClientNode()
    rclpy.spin(node)
    node.destroy_node()
    rclpy.shutdown()


if __name__ == '__main__':
    main()
