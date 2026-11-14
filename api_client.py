import requests
from config import nominatim_user_agent, opensky_user, opensky_password

class DataCollector:
    """Класс для сбора данных из внешних API OpenSky и Nominatim"""
    def __init__(self):
        self.nominatim_headers = {"User-Agent": nominatim_user_agent}
        self.opensky_auth = (opensky_user, opensky_password) if opensky_user else None

    def get_country_coordinate(self, country_name):
        """Получение географических координат стран через API Nominatim"""
        url = "https://nominatim.openstreetmap.org"
        params = {"country": country_name, "format": "json", "limit": 1}
        response = requests.get(url, params=params, headers=self.nominatim_headers)
        response.raise_for_status()
        data = response.json()
        if not data:
            raise ValueError(f"Координаты для страны '{country_name}' не найдены.")
        bbox = data[0]["boundingbox"]
        return [float(bbox[0]), float(bbox[2]), float(bbox[1]), float(bbox[3])]

    def get_aircraft_coordinate(self, bbox):
        """Получение списка самолетов в заданной области через OpenSky Network API """
        url = "https://opensky-network.org/api/states/all"
        params = {
            "lamin": bbox[0],
            "lomin": bbox[1],
            "lamax": bbox[2],
            "lomax": bbox[3]
        }
        response = requests.get(url, params=params, headers=self.nominatim_headers, auth=self.opensky_auth)
        if response.status_code == 404:
            return []
        response.raise_for_status()
        data = response.json()
        return data.get("states") or []
