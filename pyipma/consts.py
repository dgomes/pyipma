API_DISTRITS = "http://api.ipma.pt/open-data/distrits-islands.json"
API_WEATHER_TYPE = "http://api.ipma.pt/open-data/weather-type-classe.json"
API_WIND_SPEED_DAILY = "http://api.ipma.pt/open-data/wind-speed-daily-classe.json"
API_PRECIPITATION = "http://api.ipma.pt/open-data/precipitation-classe.json"
API_OBSERVATION_STATIONS = "https://api.ipma.pt/open-data/observation/meteorology/stations/stations.json"

API_OBSERVATION_OBSERVATIONS = "http://api.ipma.pt/public-data/observation/surface-stations/observations.json"
API_FORECAST_LOCATIONS = "http://api.ipma.pt/public-data/forecast/locations.json"
API_FORECAST_TEMPLATE = "http://api.ipma.pt/public-data/forecast/aggregate/{}.json"

WIND_DIRECTION = {
    'N': "Norte",
    'S': "Sul",
    'E': "Este",
    'W': "Oeste",
    'NE': "Nordeste",
    'SE': "Sudeste",
    'SW': "Sudoeste",
    'NW': "Noroeste",
    '': "",
}

WIND_DIRECTION_ID = {
    0: '',
    1: 'N',
    2: 'NE',
    3: 'E',
    4: 'SE',
    5: 'S',
    6: 'SW',
    7: 'W',
    8: 'NW',
    9: 'N'
}

WEATHER_TYPE_ID = {
    0: "No Information",
    1: "Clear sky",
    2: "Partly cloudy",
    3: "Sunny intervals",
    4: "Very cloudy",
    5: "Cloudy (High cloud)",
    6: "Showers",
    7: "Light showers",
    8: "Heavy showers",
    9: "Rain",
    10: "Light rain",
    11: "Heavy rain",
    12: "Intermittent rain",
    13: "Intermittent ligth rain",
    14: "Intermittent heavy rain",
    15: "Drizzle",
    16: "Mist",
    17: "Fog or low clouds",
    18: "Snow",
    19: "Thunderstorms",
    20: "Showers and thunderstorm.",
    21: "Hail",
    22: "Frost",
    23: "Rain and thunderstorms",
    24: "Convective clouds",
    25: "Partly cloudy",
    26: "Fog",
    27: "Cloudy"

}
