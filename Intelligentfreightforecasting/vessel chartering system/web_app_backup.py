import streamlit as st
import requests
from math import radians, sin, cos, sqrt, atan2


# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="Intelligent Freight Forecasting",
    page_icon="🚢",
    layout="wide"
)


# ============================================================
# PORT DATABASE
# ============================================================

PORTS = {

    "Chennai": {
        "country": "India",
        "latitude": 13.0827,
        "longitude": 80.2707
    },

    "Kamarajar": {
        "country": "India",
        "latitude": 13.2475,
        "longitude": 80.3440
    },

    "Mumbai": {
        "country": "India",
        "latitude": 19.0760,
        "longitude": 72.8777
    },

    "Kandla": {
        "country": "India",
        "latitude": 23.0333,
        "longitude": 70.2167
    },

    "Singapore": {
        "country": "Singapore",
        "latitude": 1.2903,
        "longitude": 103.8519
    },

    "Colombo": {
        "country": "Sri Lanka",
        "latitude": 6.9271,
        "longitude": 79.8612
    },

    "Dubai": {
        "country": "UAE",
        "latitude": 25.2048,
        "longitude": 55.2708
    },

    "Rotterdam": {
        "country": "Netherlands",
        "latitude": 51.9244,
        "longitude": 4.4777
    },

    "Shanghai": {
        "country": "China",
        "latitude": 31.2304,
        "longitude": 121.4737
    }
}


# ============================================================
# FREIGHT RATE DATABASE
# ============================================================

FREIGHT_RATES = {

    "Container":85,
    "Dry Bulk":32,
    "Liquid Bulk":45,
    "Crude Oil":52,
    "Petroleum Products":58,
    "LNG":75,
    "LPG":68,
    "Coal":30,
    "Iron Ore":28,
    "Grain":34,
    "Automobile":90,
    "General Cargo":55
}


# ============================================================
# PORT CONGESTION DATABASE
# ============================================================

PORT_CONGESTION = {

    "Chennai":62,
    "Kamarajar":58,
    "Mumbai":48,
    "Kandla":35,
    "Singapore":71,
    "Colombo":55,
    "Dubai":43,
    "Rotterdam":67,
    "Shanghai":76
}



# ============================================================
# LIVE WEATHER API
# ============================================================

def get_live_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"


    params = {

        "latitude": latitude,

        "longitude": longitude,

        "current":(
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "wind_gusts_10m,"
            "precipitation,"
            "weather_code"
        ),

        "timezone":"auto"
    }


    try:

        response = requests.get(
            url,
            params=params,
            timeout=20
        )


        response.raise_for_status()


        data = response.json()


        if "current" not in data:

            return {
                "error":
                "Weather data not returned"
            }


        current=data["current"]


        return {

            "temperature":
            current.get("temperature_2m"),

            "humidity":
            current.get("relative_humidity_2m"),

            "wind_speed":
            current.get("wind_speed_10m"),

            "wind_direction":
            current.get("wind_direction_10m"),

            "wind_gusts":
            current.get("wind_gusts_10m"),

            "precipitation":
            current.get("precipitation"),

            "weather_code":
            current.get("weather_code"),

            "time":
            current.get("time")

        }


    except requests.exceptions.Timeout:

        return {
            "error":
            "Weather API timed out"
        }


    except requests.exceptions.ConnectionError:

        return {
            "error":
            "Could not connect to weather API"
        }


    except requests.exceptions.RequestException as error:

        return {
            "error":
            str(error)
        }


    except Exception as error:

        return {
            "error":
            str(error)
        }

    # ============================================================
# WEATHER DESCRIPTION
# ============================================================

def weather_description(code):

    codes = {

        0:"Clear sky",
        1:"Mainly clear",
        2:"Partly cloudy",
        3:"Overcast",
        45:"Fog",
        51:"Light drizzle",
        53:"Moderate drizzle",
        55:"Dense drizzle",
        61:"Light rain",
        63:"Moderate rain",
        65:"Heavy rain",
        80:"Rain showers",
        81:"Moderate showers",
        82:"Heavy showers",
        95:"Thunderstorm",
        96:"Thunderstorm with hail",
        99:"Severe thunderstorm"

    }


    return codes.get(
        code,
        "Unknown"
    )



# ============================================================
# WEATHER RISK CALCULATION
# ============================================================

def calculate_weather_risk(weather):


    if not weather or "error" in weather:

        return (
            "Unavailable",
            0
        )


    wind = weather.get(
        "wind_speed"
    )


    rain = weather.get(
        "precipitation"
    )


    code = weather.get(
        "weather_code"
    )


    if wind is None:

        return (
            "Unavailable",
            0
        )


    score = 0


    # Wind risk

    if wind < 15:

        score = 10

    elif wind < 30:

        score = 30

    elif wind < 45:

        score = 60

    else:

        score = 90



    # Rain risk

    if rain:

        if rain > 10:

            score=max(score,50)

        elif rain > 5:

            score=max(score,30)



    # Storm risk

    if code in [95,96,99]:

        score=max(
            score,
            80
        )


    if score < 30:

        level="Low"

    elif score < 60:

        level="Moderate"

    elif score < 80:

        level="High"

    else:

        level="Severe"



    return (
        level,
        score
    )



# ============================================================
# PORT CONGESTION
# ============================================================

def get_port_congestion(port):


    score = PORT_CONGESTION.get(
        port,
        50
    )


    if score < 40:

        level="Low"

    elif score < 65:

        level="Moderate"

    elif score < 80:

        level="High"

    else:

        level="Severe"



    waiting_hours = (
        2 + (score/100)*46
    )


    return (
        score,
        level,
        waiting_hours
    )



# ============================================================
# FREIGHT RATE
# ============================================================

def get_freight_rate(cargo):

    return FREIGHT_RATES.get(
        cargo,
        50
    )



# ============================================================
# DISTANCE CALCULATION
# ============================================================

def calculate_distance(
        origin,
        destination
):


    lat1=radians(
        PORTS[origin]["latitude"]
    )

    lon1=radians(
        PORTS[origin]["longitude"]
    )


    lat2=radians(
        PORTS[destination]["latitude"]
    )

    lon2=radians(
        PORTS[destination]["longitude"]
    )


    dlat=lat2-lat1
    dlon=lon2-lon1


    a=(

        sin(dlat/2)**2

        +

        cos(lat1)
        *
        cos(lat2)
        *
        sin(dlon/2)**2

    )


    c=2*atan2(
        sqrt(a),
        sqrt(1-a)
    )


    distance_km=6371*c


    distance_nm=(
        distance_km*0.539957
    )


    return distance_nm



# ============================================================
# VOYAGE COST
# ============================================================

def calculate_voyage_cost(
        distance_nm,
        speed,
        daily_cost,
        port_days
):


    if speed <=0:

        return None



    sailing_days=(

        distance_nm
        /
        (speed*24)

    )


    total_days=(

        sailing_days
        +
        port_days

    )


    cost=(

        total_days
        *
        daily_cost

    )


    return {

        "sailing_days":
        sailing_days,


        "total_days":
        total_days,


        "total_cost":
        cost

    }



# ============================================================
# FREIGHT FORECAST
# ============================================================

def forecast_freight_rate(
        base_rate,
        congestion,
        weather
):


    increase=(

        (congestion/100)*0.15

        +

        (weather/100)*0.10

    )


    return (

        base_rate
        *
        (1+increase)

    )

# ============================================================
# MAIN PAGE
# ============================================================

st.title(
    "🚢 Intelligent Freight Forecasting & Vessel Chartering System"
)


st.write(
    "A data-driven decision support system for "
    "voyage cost, freight prediction, port congestion "
    "and live weather analysis."
)



# ============================================================
# SIDEBAR INPUT
# ============================================================

st.sidebar.header(
    "🚢 Voyage Parameters"
)


vessel_name = st.sidebar.text_input(
    "Vessel Name",
    "MV Ocean Star"
)


vessel_type = st.sidebar.selectbox(
    "Vessel Type",
    [
        "Container Ship",
        "Bulk Carrier",
        "Tanker",
        "LNG Carrier",
        "LPG Carrier",
        "General Cargo"
    ]
)


cargo = st.sidebar.selectbox(
    "Cargo Type",
    list(FREIGHT_RATES.keys())
)


origin = st.sidebar.selectbox(
    "Origin Port",
    list(PORTS.keys())
)


destination = st.sidebar.selectbox(
    "Destination Port",
    [
        p for p in PORTS.keys()
        if p != origin
    ]
)


quantity = st.sidebar.number_input(
    "Cargo Quantity (MT)",
    min_value=1.0,
    value=10000.0,
    step=500.0
)


speed = st.sidebar.number_input(
    "Vessel Speed (Knots)",
    min_value=1.0,
    value=14.0
)


daily_cost = st.sidebar.number_input(
    "Daily Vessel Cost ($)",
    min_value=1000.0,
    value=25000.0
)


port_days = st.sidebar.number_input(
    "Port Stay Days",
    min_value=0.0,
    value=2.0
)


analyse = st.sidebar.button(
    "🔍 ANALYSE VOYAGE",
    use_container_width=True
)



# ============================================================
# ANALYSIS
# ============================================================

if analyse:


    # Distance

    distance = calculate_distance(
        origin,
        destination
    )


    # Weather API

    origin_weather = get_live_weather(
        PORTS[origin]["latitude"],
        PORTS[origin]["longitude"]
    )


    destination_weather = get_live_weather(
        PORTS[destination]["latitude"],
        PORTS[destination]["longitude"]
    )



    origin_risk, origin_score = calculate_weather_risk(
        origin_weather
    )


    destination_risk, destination_score = calculate_weather_risk(
        destination_weather
    )


    weather_score=max(
        origin_score,
        destination_score
    )


    if weather_score < 30:
        weather_level="Low"

    elif weather_score < 60:
        weather_level="Moderate"

    elif weather_score < 80:
        weather_level="High"

    else:
        weather_level="Severe"



    # Congestion

    origin_congestion, origin_level, origin_wait = get_port_congestion(
        origin
    )


    destination_congestion, destination_level, destination_wait = get_port_congestion(
        destination
    )


    total_wait = (
        origin_wait
        +
        destination_wait
    )


    total_port_days = (
        port_days
        +
        total_wait/24
    )



    # Cost

    voyage = calculate_voyage_cost(
        distance,
        speed,
        daily_cost,
        total_port_days
    )



    # Freight

    base_rate=get_freight_rate(
        cargo
    )


    forecast_rate=forecast_freight_rate(
        base_rate,
        max(
            origin_congestion,
            destination_congestion
        ),
        weather_score
    )


    freight_cost = (
        forecast_rate
        *
        quantity
    )



    total_cost = (
        voyage["total_cost"]
        +
        freight_cost
    )



    # ========================================================
    # SUMMARY
    # ========================================================

    st.divider()

    st.header(
        "📋 Voyage Summary"
    )


    c1,c2,c3,c4=st.columns(4)


    c1.metric(
        "Vessel",
        vessel_name
    )


    c2.metric(
        "Cargo",
        cargo
    )


    c3.metric(
        "Quantity",
        f"{quantity:,.0f} MT"
    )


    c4.metric(
        "Route",
        f"{origin} → {destination}"
    )



    # ========================================================
    # WEATHER
    # ========================================================

    st.header(
        "🌦️ Live Weather Analysis"
    )


    col1,col2=st.columns(2)



    with col1:

        st.subheader(
            origin
        )


        if "error" not in origin_weather:


            st.metric(
                "Temperature",
                f"{origin_weather['temperature']} °C"
            )


            st.metric(
                "Wind Speed",
                f"{origin_weather['wind_speed']} km/h"
            )


            st.write(
                "Condition:",
                weather_description(
                    origin_weather["weather_code"]
                )
            )


            st.write(
                "Risk:",
                origin_risk
            )


            st.caption(
                origin_weather["time"]
            )


        else:

            st.warning(
                "Live weather unavailable"
            )

            st.code(
                origin_weather["error"]
            )



    with col2:

        st.subheader(
            destination
        )


        if "error" not in destination_weather:


            st.metric(
                "Temperature",
                f"{destination_weather['temperature']} °C"
            )


            st.metric(
                "Wind Speed",
                f"{destination_weather['wind_speed']} km/h"
            )


            st.write(
                "Condition:",
                weather_description(
                    destination_weather["weather_code"]
                )
            )


            st.write(
                "Risk:",
                destination_risk
            )


            st.caption(
                destination_weather["time"]
            )


        else:

            st.warning(
                "Live weather unavailable"
            )

            st.code(
                destination_weather["error"]
            )



    st.info(
        f"Overall Weather Risk: {weather_level} "
        f"({weather_score}/100)"
    )



    # ========================================================
    # CONGESTION
    # ========================================================

    st.header(
        "⚓ Port Congestion"
    )


    c1,c2=st.columns(2)


    c1.metric(
        origin,
        f"{origin_level} ({origin_congestion}/100)"
    )


    c2.metric(
        destination,
        f"{destination_level} ({destination_congestion}/100)"
    )


    st.write(
        f"Estimated waiting time: "
        f"{total_wait:.1f} hours"
    )



    # ========================================================
    # COST SUMMARY
    # ========================================================

    st.header(
        "💰 Cost Analysis"
    )


    c1,c2,c3=st.columns(3)


    c1.metric(
        "Voyage Cost",
        f"${voyage['total_cost']:,.2f}"
    )


    c2.metric(
        "Freight Cost",
        f"${freight_cost:,.2f}"
    )


    c3.metric(
        "Total Project Cost",
        f"${total_cost:,.2f}"
    )



    # ========================================================
    # DOWNLOAD REPORT
    # ========================================================

    report=f"""

INTELLIGENT FREIGHT FORECASTING SYSTEM
======================================

Vessel:
{vessel_name}

Type:
{vessel_type}

Cargo:
{cargo}

Quantity:
{quantity} MT


Route:
{origin} -> {destination}


Distance:
{distance:.2f} NM


Weather Risk:
{weather_level}


Freight Rate:
${forecast_rate:.2f}/MT


Voyage Cost:
${voyage['total_cost']:.2f}


Freight Cost:
${freight_cost:.2f}


TOTAL PROJECT COST:
${total_cost:.2f}

"""


    st.download_button(
        "📄 Download Report",
        report,
        file_name="voyage_report.txt"
    )



else:

    st.info(
        "Enter voyage details and click Analyse Voyage"
    )



st.divider()

st.caption(
    "🚢 Intelligent Freight Forecasting System | "
    "Live Weather powered by Open-Meteo"
)
