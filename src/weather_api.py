import requests
import json
import os
from datetime import datetime, timedelta

# WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")  # a719506c7c8549459ae205820250803
# BASE_URL = "http://api.weatherapi.com/v1"

class WeatherApi:
    def __init__(self):
        self.weather_api_key = "a719506c7c8549459ae205820250803"
        self.base_url = "http://api.weatherapi.com/v1"

    def get_weather_data(self, location: str, start_date: str, end_date: str):
        """
        Coletar os dados da api de históricos climáticos de um período.
        
        location: Local
        start_date: data inicial
        end_date: data final
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
    
    # with open(f"../data/json/weather_{location}.json", "w") as file:
    #     file.write(json.dumps(data, indent=4))
