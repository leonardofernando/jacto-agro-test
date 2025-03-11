import requests
import json
from datetime import datetime, timedelta
from typing import List, Dict


class WeatherApi:
    """Classe para coletar dados climáticos históricos utilizando a API WeatherAPI."""

    def __init__(self):
        self.weather_api_key = "a719506c7c8549459ae205820250803"  # os.getenv("WEATHER_API_KEY")
        self.base_url = "http://api.weatherapi.com/v1"

    def get_weather_data(self, location: str, start_date: str, end_date: str) -> List[Dict]:
        """
        Coleta dados climáticos históricos para um local e período específico.
        
        Args:
            location (str): Localização para consulta.
            start_date (str): Data inicial no formato "YYYY-MM-DD".
            end_date (str): Data final no formato "YYYY-MM-DD".
        
        Returns:
            list: Lista de dicionários contendo dados climáticos diários.
        """
        weather_data = []

        date = datetime.strptime(start_date, "%Y-%m-%d")
        end_date = datetime.strptime(end_date, "%Y-%m-%d")

        while date <= end_date:
            format_date = date.strftime("%Y-%m-%d")
            weather_api_url = f"{self.base_url}/history.json?key={self.weather_api_key}&q={location}&dt={format_date}"

            try:
                response = requests.get(weather_api_url)
                response.raise_for_status()
                data = response.json()

                if "forecast" in data:
                    forecastday = data.get("forecast").get("forecastday")[0].get("day")
                    info = {
                        "data": format_date,
                        "local": location,
                        "estado": data.get("location").get("region"),
                        "temperatura": forecastday.get("avgtemp_c"),
                        "humidade": forecastday.get("avghumidity"),
                        "precipitacao": forecastday.get("totalprecip_mm"),
                        "velocidade_do_vento": forecastday.get("maxwind_kph"),
                    }
                    weather_data.append(info)

            except requests.exceptions.RequestException as e:
                print(f"Erro na busca de dados do dia {format_date}: {e}")

            date += timedelta(days=1)
        
        return weather_data


if __name__ == "__main__":
    location = "Curitiba"
    start_date = "2025-03-02"
    end_date = "2025-03-09"
    
    data = WeatherApi().get_weather_data(location=location, start_date=start_date, end_date=end_date)
    print(f"{data}")
    
    with open(f"../data/json/weather_{location}.json", "w") as file:
        file.write(json.dumps(data, indent=4))
