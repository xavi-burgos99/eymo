import os

import requests
from dotenv import load_dotenv

load_dotenv(dotenv_path="../static/.env")


class HomeAssistant:
    def __init__(self, base_url, token):
        self.base_url = base_url
        self.token = token
        self.headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json",
        }

    def _get(self, endpoint):
        url = f"{self.base_url}{endpoint}"
        response = requests.get(url, headers=self.headers)
        response.raise_for_status()
        return response.json()

    def _post(self, endpoint, data):
        url = f"{self.base_url}{endpoint}"
        response = requests.post(url, headers=self.headers, json=data)
        response.raise_for_status()
        return response.json()

    def get_all_entities(self):
        """
        Get all entities in Home Assistant.
        """
        return self._get("/api/states")

    def get_light_entities(self):
        """
        Get all light entities in Home Assistant.
        """
        entities = self.get_all_entities()
        return [entity for entity in entities if entity['entity_id'].startswith('light.')]

    def get_sensor_entities(self):
        """
        Get all sensor entities in Home Assistant.
        """
        entities = self.get_all_entities()
        return [entity for entity in entities if entity['entity_id'].startswith('sensor.')]

    def turn_on_light(self, entity_id):
        """
        Turn on a specific light entity in Home Assistant.
        """
        data = {"entity_id": entity_id}
        return self._post("/api/services/light/turn_on", data)

    def turn_off_light(self, entity_id):
        """
        Turn off a specific light entity in Home Assistant.
        """
        data = {"entity_id": entity_id}
        return self._post("/api/services/light/turn_off", data)

    def get_entity_state(self, entity_id):
        """
        Get the state of a specific entity in Home Assistant.
        """
        return self._get(f"/api/states/{entity_id}")

    # AREAS #
    def get_areas(self):
        """
        Get all areas in Home Assistant.
        """
        return self._post("/api/template", {"template": "{{ areas() | to_json }}"})

    def get_area_name(self, lookup_value):
        """
        Get the name of a specific area in Home Assistant.
        """
        return self._post("/api/template", {"template": f"{{{{ area_name('{lookup_value}') | to_json }}}}"})

    def get_area_id(self, lookup_value):
        """
        Get the id of a specific area in Home Assistant.
        """
        return self._post("/api/template", {"template": f"{{{{ area_id('{lookup_value}') | to_json }}}}"})

    def get_entity_area(self, entity_id):
        """
        Get the area of a specific entity in Home Assistant.
        """
        return self._post("/api/template", {"template": f"{{{{ area_id('{entity_id}') | to_json }}}}"})

    def get_area_entities(self, area_id):
        """
        Get all entities in a specific area in Home Assistant.
        """
        return self._post("/api/template", {"template": f"{{{{ area_entities('{area_id}') | to_json }}}}"})

    def get_area_devices(self, area_id):
        """
        Get all devices in a specific area in Home Assistant.
        """
        return self._post("/api/template", {"template": f"{{{{ area_devices('{area_id}') | to_json }}}}"})


# Ejemplo de uso:
if __name__ == "__main__":
    base_url = os.getenv("HA_BASE_URL")
    token = os.getenv("HA_TOKEN")

    ha_helper = HomeAssistant(base_url, token)

    print(ha_helper.get_areas())
    print(ha_helper.get_entity_area("light.smart_light_strip"))
    print(ha_helper.get_area_devices("gaming_room"))
    print(ha_helper.get_area_name("garatge"))
