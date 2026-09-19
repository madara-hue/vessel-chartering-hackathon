import pandas as pd


def get_weather_data(weather_file, port_name):

    try:
        weather = pd.read_csv(weather_file)

        result = weather[
            weather["Port_Name"].astype(str).str.lower()
            == port_name.lower()
        ]

        if result.empty:
            return None

        return result.iloc[0]

    except Exception as error:
        print("Weather data error:", error)
        return None


def calculate_weather_score(weather_data):

    if weather_data is None:
        return 0

    wind = float(weather_data["Wind_Speed_Knots"])
    wave = float(weather_data["Wave_Height_M"])
    visibility = float(weather_data["Visibility_KM"])

    # Wind score
    if wind <= 10:
        wind_score = 100
    elif wind <= 15:
        wind_score = 85
    elif wind <= 20:
        wind_score = 70
    elif wind <= 25:
        wind_score = 50
    else:
        wind_score = 30

    # Wave score
    if wave <= 1.0:
        wave_score = 100
    elif wave <= 1.5:
        wave_score = 85
    elif wave <= 2.0:
        wave_score = 70
    elif wave <= 3.0:
        wave_score = 50
    else:
        wave_score = 30

    # Visibility score
    if visibility >= 10:
        visibility_score = 100
    elif visibility >= 8:
        visibility_score = 85
    elif visibility >= 5:
        visibility_score = 70
    elif visibility >= 3:
        visibility_score = 50
    else:
        visibility_score = 30

    weather_score = (
        wind_score * 0.40
        + wave_score * 0.40
        + visibility_score * 0.20
    )

    return weather_score