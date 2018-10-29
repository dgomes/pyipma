API_DISTRITS = "http://api.ipma.pt/open-data/distrits-islands.json"
API_FORECAST = "http://api.ipma.pt/open-data/forecast/meteorology/cities/daily/"
API_OBSERVATION_STATIONS = "http://api.ipma.pt/public-data/observation/surface-stations/stations.json"
API_OBSERVATION_OBSERVATIONS = "http://api.ipma.pt/public-data/observation/surface-stations/observations.json"
API_WEATHER_TYPE = "http://api.ipma.pt/open-data/weather-type-classe.json"
API_WIND_TYPE = "http://api.ipma.pt/open-data/wind-speed-daily-classe.json"

#deprecated
#API_OBSERVATION = "http://pda.ipma.pt/observacao.jsp"
#API_XML_OBSERVATION = "http://www.ipma.pt/resources.www/internal.user/pw_hh_pt.xml"

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
    1: 'S',
    2: 'SW',
    3: 'W',
    4: 'NW',
    5: 'N',
    6: 'NE',
    7: 'E',
    8: 'SE',
    9: 'S'
}
