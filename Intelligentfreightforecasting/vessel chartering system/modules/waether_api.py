import requests


# ============================================================
# PORT COORDINATES
# ============================================================

PORT_COORDINATES = {

    "Kamarajar": (13.2330, 80.3330),

    "Chennai": (13.0827, 80.2707),

    "Krishnapatnam": (14.2550, 80.1230),

    "Kakinada": (16.9891, 82.2475),

    "Visakhapatnam": (17.6868, 83.2185),

    "Paradip": (20.2961, 86.6117),

    "Haldia": (22.0257, 88.0583),

    "Kolkata": (22.5726, 88.3639)
}


# ============================================================
# WEATHER CODE
# ============================================================

def weather_description(code):

    codes = {

        0: "Clear sky",

        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",

        45: "Fog",
        48: "Depositing rime fog",

        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",

        61: "Slight rain",
        63: "Moderate rain",
        65: "Heavy rain",

        71: "Slight snow",
        73: "Moderate snow",
        75: "Heavy snow",

        80: "Slight rain showers",
        81: "Moderate rain showers",
        82: "Violent rain showers",

        95: "Thunderstorm",

        96: "Thunderstorm with hail",
        99: "Severe thunderstorm with hail"
    }

    return codes.get(
        int(code),
        "Unknown"
    )


# ============================================================
# GET LIVE WEATHER
# ============================================================

def get_live_weather(port_name):

    if port_name not in PORT_COORDINATES:

        return None


    latitude, longitude = (
        PORT_COORDINATES[port_name]
    )


    url = (
        "https://api.open-meteo.com/v1/forecast"
    )


    params = {

        "latitude": latitude,

        "longitude": longitude,

        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "precipitation,"
            "weather_code,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "wind_gusts_10m"
        ),

        "wind_speed_unit": "kn",

        "temperature_unit": "celsius",

        "precipitation_unit": "mm",

        "timezone": "Asia/Kolkata"
    }


    try:

        response = requests.get(
            url,
            params=params,
            timeout=15
        )

        response.raise_for_status()

        data = response.json()

        current = data.get(
            "current",
            {}
        )


        return {

            "temperature_2m":
                current.get(
                    "temperature_2m"
                ),

            "relative_humidity_2m":
                current.get(
                    "relative_humidity_2m"
                ),

            "precipitation":
                current.get(
                    "precipitation"
                ),

            "weather_code":
                current.get(
                    "weather_code"
                ),

            "weather_condition":
                weather_description(
                    current.get(
                        "weather_code",
                        0
                    )
                ),

            "wind_speed_10m":
                current.get(
                    "wind_speed_10m"
                ),

            "wind_direction_10m":
                current.get(
                    "wind_direction_10m"
                ),

            "wind_gusts_10m":
                current.get(
                    "wind_gusts_10m"
                ),

            "time":
                current.get(
                    "time"
                )
        }


    except Exception as error:

        print(
            "Weather API error:",
            error
        )

        return None