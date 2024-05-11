import httpx
from typing import Any, Dict, Optional


class BaseApi:
    def __init__(self, base_url: str):
        self.base_url = base_url
        self.session = httpx.AsyncClient()

    async def __aenter__(self):
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.session.aclose()

    def add_headers(self, custom_headers: Dict[str, str]):
        """
        Agrega encabezados personalizados a la sesión HTTP.
        """
        for key, value in custom_headers.items():
            self.session.headers[key] = value

    async def send_request(self, method: str, endpoint: str, params: Optional[Dict[str, Any]] = None, data: Optional[Dict[str, Any]] = None, headers: Optional[Dict[str, str]] = None) -> httpx.Response:
        """
        Envía una solicitud HTTP a la API con el método, endpoint y datos proporcionados.
        """
        url = f"{self.base_url}{endpoint}"
        response = await self.session.request(method=method, url=url, params=params, json=data, headers=headers)
        return response
