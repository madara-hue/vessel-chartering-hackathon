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
# STORED PORT DATA
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
# FREIGHT RATE DATA
# ============================================================

FREIGHT_RATES = {
    "Container": 85,
    "Dry Bulk": 32,
    "Liquid Bulk": 45,
    "Crude Oil": 52,
    "Petroleum Products": 58,
    "LNG": 75,
    "LPG": 68,
    "Coal": 30,
    "Iron Ore": 28,
    "Grain": 34,
    "Automobile": 90,
    "General Cargo": 55
}


# ============================================================
# PORT CONGESTION DATA
# ============================================================

PORT_CONGESTION = {
    "Chennai": 62,
    "Kamarajar": 58,
    "Mumbai": 48,
    "Kandla": 35,
    "Singapore": 71,
    "Colombo": 55,
    "Dubai": 43,
    "Rotterdam": 67,
    "Shanghai": 76
}


# ============================================================
# LIVE WEATHER FUNCTION
# ============================================================

# ============================================================
# LIVE WEATHER
# ============================================================

def get_live_weather(latitude, longitude):

    url = "https://api.open-meteo.com/v1/forecast"

    params = {
        "latitude": latitude,
        "longitude": longitude,
        "current": (
            "temperature_2m,"
            "relative_humidity_2m,"
            "wind_speed_10m,"
            "wind_direction_10m,"
            "wind_gusts_10m,"
            "precipitation,"
            "weather_code"
        ),
        "temperature_unit": "celsius",
        "wind_speed_unit": "kmh",
        "precipitation_unit": "mm",
        "timezone": "auto"
    }

    try:

        response = requests.get(
            url,
            params=params,
            timeout=20
        )

        # Check HTTP response
        response.raise_for_status()

        data = response.json()

        # Check that current weather exists
        if "current" not in data:

            return {
                "error": "Weather API returned no current weather data.",
                "api_response": data
            }

        current = data["current"]

        return {
            "temperature": current.get(
                "temperature_2m"
            ),

            "humidity": current.get(
                "relative_humidity_2m"
            ),

            "wind_speed": current.get(
                "wind_speed_10m"
            ),

            "wind_direction": current.get(
                "wind_direction_10m"
            ),

            "wind_gusts": current.get(
                "wind_gusts_10m"
            ),

            "precipitation": current.get(
                "precipitation"
            ),

            "weather_code": current.get(
                "weather_code"
            ),

            "time": current.get(
                "time"
            )
        }

    except requests.exceptions.Timeout:

        return {
            "error": "Weather API request timed out."
        }

    except requests.exceptions.ConnectionError:

        return {
            "error": "Could not connect to the weather API."
        }

    except requests.exceptions.HTTPError as error:

        return {
            "error": f"Weather API HTTP error: {error}"
        }

    except Exception as error:

        return {
            "error": f"Weather API error: {error}"
        }

    


# ============================================================
# WEATHER DESCRIPTION
# ============================================================

def weather_description(code):

    weather_codes = {
        0: "Clear sky",
        1: "Mainly clear",
        2: "Partly cloudy",
        3: "Overcast",
        45: "Fog",
        48: "Depositing rime fog",
        51: "Light drizzle",
        53: "Moderate drizzle",
        55: "Dense drizzle",
        61: "Light rain",
        63: "Moderate rain",
        65: "Heavy rain",
        71: "Light snow",
        73: "Moderate snow",
        75: "Heavy snow",
        80: "Light rain showers",
        81: "Moderate rain showers",
        82: "Heavy rain showers",
        95: "Thunderstorm",
        96: "Thunderstorm with hail",
        99: "Thunderstorm with heavy hail"
    }

    return weather_codes.get(code, "Unknown")


# ============================================================
# WEATHER RISK
# ============================================================

def calculate_weather_risk(weather):

    if not weather or "error" in weather:
        return "Unavailable", 0

    wind_speed = weather.get("wind_speed")
    precipitation = weather.get("precipitation")
    weather_code = weather.get("weather_code")

    if wind_speed is None:
        return "Unavailable", 0

    # Wind risk
    if wind_speed < 15:
        wind_score = 10
    elif wind_speed < 30:
        wind_score = 30
    elif wind_speed < 45:
        wind_score = 60
    else:
        wind_score = 90

    # Rain risk
    weather_score = 0

    if precipitation is not None:

        if precipitation > 10:
            weather_score = 30

        elif precipitation > 5:
            weather_score = 20

        elif precipitation > 1:
            weather_score = 10

    # Thunderstorm risk
    if weather_code in [95, 96, 99]:

        weather_score = max(
            weather_score,
            70
        )

    final_score = max(
        wind_score,
        weather_score
    )

    if final_score < 30:
        level = "Low"

    elif final_score < 60:
        level = "Moderate"

    elif final_score < 80:
        level = "High"

    else:
        level = "Severe"

    return level, final_score


# ============================================================
# PORT CONGESTION
# ============================================================

def get_port_congestion(port):

    value = PORT_CONGESTION.get(
        port,
        50
    )

    if value < 40:
        level = "Low"

    elif value < 65:
        level = "Moderate"

    elif value < 80:
        level = "High"

    else:
        level = "Severe"

    # Estimated waiting time
    waiting_hours = 2 + (value / 100) * 46

    return (
        value,
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

    lat1 = radians(
        PORTS[origin]["latitude"]
    )

    lon1 = radians(
        PORTS[origin]["longitude"]
    )

    lat2 = radians(
        PORTS[destination]["latitude"]
    )

    lon2 = radians(
        PORTS[destination]["longitude"]
    )

    dlat = lat2 - lat1
    dlon = lon2 - lon1

    a = (
        sin(dlat / 2) ** 2
        +
        cos(lat1)
        *
        cos(lat2)
        *
        sin(dlon / 2) ** 2
    )

    c = 2 * atan2(
        sqrt(a),
        sqrt(1 - a)
    )

    earth_radius_km = 6371

    distance_km = (
        earth_radius_km * c
    )

    distance_nm = (
        distance_km * 0.539957
    )

    return distance_nm


# ============================================================
# VOYAGE COST
# ============================================================

def calculate_voyage_cost(
    distance_nm,
    vessel_speed,
    daily_cost,
    port_days
):

    if vessel_speed <= 0:
        return None

    sailing_days = (
        distance_nm /
        (vessel_speed * 24)
    )

    total_days = (
        sailing_days +
        port_days
    )

    total_cost = (
        total_days *
        daily_cost
    )

    return {
        "sailing_days": sailing_days,
        "total_days": total_days,
        "total_cost": total_cost
    }


# ============================================================
# FREIGHT FORECAST
# ============================================================

def forecast_freight_rate(
    base_rate,
    congestion_score,
    weather_risk_score
):

    congestion_effect = (
        congestion_score / 100
    ) * 0.15

    weather_effect = (
        weather_risk_score / 100
    ) * 0.10

    forecast_rate = (
        base_rate *
        (
            1 +
            congestion_effect +
            weather_effect
        )
    )

    return forecast_rate


# ============================================================
# MAIN PAGE
# ============================================================

st.title(
    "🚢 Intelligent Freight Forecasting & "
    "Vessel Chartering System"
)

st.write(
    "A data-driven decision-support system "
    "for analysing voyage costs, freight rates, "
    "port congestion and live weather."
)


# ============================================================
# SIDEBAR
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

destination_options = [
    port
    for port in PORTS.keys()
    if port != origin
]

destination = st.sidebar.selectbox(
    "Destination Port",
    destination_options
)

cargo_quantity = st.sidebar.number_input(
    "Cargo Quantity (tonnes)",
    min_value=1.0,
    value=10000.0,
    step=500.0
)

vessel_speed = st.sidebar.number_input(
    "Vessel Speed (knots)",
    min_value=1.0,
    value=14.0,
    step=0.5
)

daily_cost = st.sidebar.number_input(
    "Daily Vessel Cost ($)",
    min_value=100.0,
    value=25000.0,
    step=1000.0
)

port_days = st.sidebar.number_input(
    "Additional Port Stay (days)",
    min_value=0.0,
    value=2.0,
    step=0.5
)

analyse = st.sidebar.button(
    "🔍 ANALYSE VOYAGE",
    use_container_width=True
)


# ============================================================
# ANALYSIS
# ============================================================

if analyse:

    # ========================================================
    # DISTANCE
    # ========================================================

    distance_nm = calculate_distance(
        origin,
        destination
    )


    # ========================================================
    # LIVE WEATHER
    # ========================================================

    origin_weather = get_live_weather(
        PORTS[origin]["latitude"],
        PORTS[origin]["longitude"]
    )

    destination_weather = get_live_weather(
        PORTS[destination]["latitude"],
        PORTS[destination]["longitude"]
    )


    # ========================================================
    # WEATHER RISK
    # ========================================================

    origin_risk, origin_score = (
        calculate_weather_risk(
            origin_weather
        )
    )

    destination_risk, destination_score = (
        calculate_weather_risk(
            destination_weather
        )
    )

    overall_weather_score = max(
        origin_score,
        destination_score
    )

    if overall_weather_score < 30:
        overall_weather = "Low"

    elif overall_weather_score < 60:
        overall_weather = "Moderate"

    elif overall_weather_score < 80:
        overall_weather = "High"

    else:
        overall_weather = "Severe"


    # ========================================================
    # PORT CONGESTION
    # ========================================================

    (
        origin_congestion_score,
        origin_congestion_level,
        origin_waiting_hours
    ) = get_port_congestion(origin)

    (
        destination_congestion_score,
        destination_congestion_level,
        destination_waiting_hours
    ) = get_port_congestion(destination)

    total_waiting_hours = (
        origin_waiting_hours +
        destination_waiting_hours
    )

    total_waiting_days = (
        total_waiting_hours / 24
    )


    # ========================================================
    # TOTAL PORT TIME
    # ========================================================

    total_port_days = (
        port_days +
        total_waiting_days
    )


    # ========================================================
    # VOYAGE COST
    # ========================================================

    voyage = calculate_voyage_cost(
        distance_nm,
        vessel_speed,
        daily_cost,
        total_port_days
    )


    # ========================================================
    # FREIGHT RATE
    # ========================================================

    base_freight_rate = get_freight_rate(
        cargo
    )

    forecast_rate = forecast_freight_rate(
        base_freight_rate,
        max(
            origin_congestion_score,
            destination_congestion_score
        ),
        overall_weather_score
    )

    freight_cost = (
        forecast_rate *
        cargo_quantity
    )


    # ========================================================
    # TOTAL PROJECT COST
    # ========================================================

    if voyage:

        total_project_cost = (
            voyage["total_cost"] +
            freight_cost
        )

    else:

        total_project_cost = 0


    # ========================================================
    # VOYAGE SUMMARY
    # ========================================================

    st.divider()

    st.header(
        "📋 Voyage Summary"
    )

    c1, c2, c3, c4 = st.columns(4)

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
        f"{cargo_quantity:,.0f} MT"
    )

    c4.metric(
        "Route",
        f"{origin} → {destination}"
    )


    # ========================================================
    # ROUTE ANALYSIS
    # ========================================================

    st.header(
        "🗺️ Route Analysis"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Distance",
        f"{distance_nm:,.0f} NM"
    )

    c2.metric(
        "Vessel Speed",
        f"{vessel_speed:.1f} knots"
    )

    c3.metric(
        "Sailing Time",
        f"{voyage['sailing_days']:.2f} days"
        if voyage
        else "N/A"
    )


    # ========================================================
    # LIVE WEATHER
    # ========================================================

    st.header(
        "🌦️ Live Weather Analysis"
    )

    weather_col1, weather_col2 = (
        st.columns(2)
    )


    # ========================================================
    # ORIGIN WEATHER
    # ========================================================

    with weather_col1:

        st.subheader(
            f"🌊 {origin}"
        )

        if (
            origin_weather
            and "error" not in origin_weather
        ):

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Temperature",
                f"{origin_weather['temperature']} °C"
            )

            c2.metric(
                "Wind",
                f"{origin_weather['wind_speed']} km/h"
            )

            c3.metric(
                "Rain",
                f"{origin_weather['precipitation']} mm"
            )

            st.write(
                "**Condition:** "
                +
                weather_description(
                    origin_weather["weather_code"]
                )
            )

            st.write(
                "**Humidity:** "
                f"{origin_weather['humidity']}%"
            )

            st.write(
                "**Wind Direction:** "
                f"{origin_weather['wind_direction']}°"
            )

            st.write(
                "**Wind Gusts:** "
                f"{origin_weather['wind_gusts']} km/h"
            )

            st.write(
                "**Weather Risk:** "
                f"{origin_risk}"
            )

            st.write(
                "**Weather Risk Score:** "
                f"{origin_score}/100"
            )

            st.caption(
                f"Updated: {origin_weather['time']}"
            )

        else:

            st.warning(
                f"Live weather unavailable for {origin}."
            )

            if "error" in origin_weather:

                st.caption(
                    f"Error: {origin_weather['error']}"
                )


    # ========================================================
    # DESTINATION WEATHER
    # ========================================================

    with weather_col2:

        st.subheader(
            f"🌊 {destination}"
        )

        if (
            destination_weather
            and "error" not in destination_weather
        ):

            c1, c2, c3 = st.columns(3)

            c1.metric(
                "Temperature",
                f"{destination_weather['temperature']} °C"
            )

            c2.metric(
                "Wind",
                f"{destination_weather['wind_speed']} km/h"
            )

            c3.metric(
                "Rain",
                f"{destination_weather['precipitation']} mm"
            )

            st.write(
                "**Condition:** "
                +
                weather_description(
                    destination_weather["weather_code"]
                )
            )

            st.write(
                "**Humidity:** "
                f"{destination_weather['humidity']}%"
            )

            st.write(
                "**Wind Direction:** "
                f"{destination_weather['wind_direction']}°"
            )

            st.write(
                "**Wind Gusts:** "
                f"{destination_weather['wind_gusts']} km/h"
            )

            st.write(
                "**Weather Risk:** "
                f"{destination_risk}"
            )

            st.write(
                "**Weather Risk Score:** "
                f"{destination_score}/100"
            )

            st.caption(
                f"Updated: {destination_weather['time']}"
            )

        else:

            st.warning(
                f"Live weather unavailable for {destination}."
            )

            if "error" in destination_weather:

                st.caption(
                    f"Error: {destination_weather['error']}"
                )


    # ========================================================
    # WEATHER SUMMARY
    # ========================================================

    st.info(
        f"Overall Weather Risk: "
        f"**{overall_weather}** "
        f"({overall_weather_score}/100)"
    )


    # ========================================================
    # PORT CONGESTION
    # ========================================================

    st.header(
        "⚓ Port Congestion & Waiting Time"
    )

    congestion_col1, congestion_col2 = (
        st.columns(2)
    )


    with congestion_col1:

        st.subheader(
            origin
        )

        st.metric(
            "Congestion Score",
            f"{origin_congestion_score}/100"
        )

        st.write(
            f"Congestion Level: "
            f"**{origin_congestion_level}**"
        )

        st.write(
            f"Estimated Waiting Time: "
            f"**{origin_waiting_hours:.1f} hours**"
        )


    with congestion_col2:

        st.subheader(
            destination
        )

        st.metric(
            "Congestion Score",
            f"{destination_congestion_score}/100"
        )

        st.write(
            f"Congestion Level: "
            f"**{destination_congestion_level}**"
        )

        st.write(
            f"Estimated Waiting Time: "
            f"**{destination_waiting_hours:.1f} hours**"
        )


    st.info(
        f"Total estimated port waiting time: "
        f"**{total_waiting_hours:.1f} hours "
        f"({total_waiting_days:.2f} days)**"
    )


    # ========================================================
    # FREIGHT FORECAST
    # ========================================================

    st.header(
        "📈 Freight Rate Forecast"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Base Freight Rate",
        f"${base_freight_rate:,.2f}/MT"
    )

    c2.metric(
        "Forecast Freight Rate",
        f"${forecast_rate:,.2f}/MT"
    )

    c3.metric(
        "Freight Cost",
        f"${freight_cost:,.2f}"
    )

    st.write(
        "The forecast adjusts the stored base freight "
        "rate using port congestion and current weather risk."
    )


    # ========================================================
    # VOYAGE COST
    # ========================================================

    st.header(
        "💵 Voyage Cost Analysis"
    )

    if voyage:

        c1, c2, c3 = st.columns(3)

        c1.metric(
            "Sailing Time",
            f"{voyage['sailing_days']:.2f} days"
        )

        c2.metric(
            "Total Port Time",
            f"{total_port_days:.2f} days"
        )

        c3.metric(
            "Voyage Cost",
            f"${voyage['total_cost']:,.2f}"
        )


    # ========================================================
    # TOTAL COST SUMMARY
    # ========================================================

    st.header(
        "💰 Total Cost Summary"
    )

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "Voyage Cost",
        f"${voyage['total_cost']:,.2f}"
        if voyage
        else "$0.00"
    )

    c2.metric(
        "Freight Cost",
        f"${freight_cost:,.2f}"
    )

    c3.metric(
        "TOTAL PROJECT COST",
        f"${total_project_cost:,.2f}"
    )


    # ========================================================
    # DECISION SUMMARY
    # ========================================================

    st.header(
        "🎯 Decision Summary"
    )

    st.success(
        "Voyage analysis completed successfully."
    )

    summary_data = {
        "Vessel": vessel_name,
        "Vessel Type": vessel_type,
        "Cargo": cargo,
        "Quantity": f"{cargo_quantity:,.0f} MT",
        "Route": f"{origin} → {destination}",
        "Distance": f"{distance_nm:,.0f} NM",
        "Weather Risk": overall_weather,
        "Weather Score": f"{overall_weather_score}/100",
        "Origin Congestion": origin_congestion_level,
        "Destination Congestion": destination_congestion_level,
        "Total Waiting": f"{total_waiting_days:.2f} days",
        "Forecast Freight": f"${forecast_rate:,.2f}/MT",
        "Voyage Cost": (
            f"${voyage['total_cost']:,.2f}"
            if voyage
            else "$0.00"
        ),
        "Freight Cost": f"${freight_cost:,.2f}",
        "Total Project Cost": f"${total_project_cost:,.2f}"
    }

    summary_df = {
        "Parameter": list(summary_data.keys()),
        "Value": list(summary_data.values())
    }

    st.dataframe(
        summary_df,
        use_container_width=True,
        hide_index=True
    )


    # ========================================================
    # DOWNLOAD REPORT
    # ========================================================

    st.header(
        "📥 Download Report"
    )

    report = f"""
INTELLIGENT FREIGHT FORECASTING
& VESSEL CHARTERING SYSTEM
==========================================

VOYAGE DETAILS
------------------------------------------
Vessel: {vessel_name}
Vessel Type: {vessel_type}
Cargo: {cargo}
Quantity: {cargo_quantity:,.0f} MT

Origin: {origin}
Destination: {destination}

ROUTE
------------------------------------------
Distance: {distance_nm:,.0f} NM
Vessel Speed: {vessel_speed:.1f} knots
Sailing Days: {voyage['sailing_days']:.2f}

LIVE WEATHER
------------------------------------------
Overall Risk: {overall_weather}
Weather Score: {overall_weather_score}/100

Origin Risk: {origin_risk}
Origin Score: {origin_score}/100

Destination Risk: {destination_risk}
Destination Score: {destination_score}/100

PORT CONGESTION
------------------------------------------
Origin:
Congestion: {origin_congestion_level}
Score: {origin_congestion_score}/100
Waiting: {origin_waiting_hours:.1f} hours

Destination:
Congestion: {destination_congestion_level}
Score: {destination_congestion_score}/100
Waiting: {destination_waiting_hours:.1f} hours

Total Waiting:
{total_waiting_hours:.1f} hours
{total_waiting_days:.2f} days

FREIGHT
------------------------------------------
Base Rate: ${base_freight_rate:,.2f}/MT
Forecast Rate: ${forecast_rate:,.2f}/MT
Freight Cost: ${freight_cost:,.2f}

VOYAGE COST
------------------------------------------
Sailing Days: {voyage['sailing_days']:.2f}
Total Port Days: {total_port_days:.2f}
Voyage Cost: ${voyage['total_cost']:,.2f}

TOTAL PROJECT COST
------------------------------------------
${total_project_cost:,.2f}

Generated by:
Intelligent Freight Forecasting System
"""

    st.download_button(
        label="📄 Download Voyage Report",
        data=report,
        file_name="voyage_report.txt",
        mime="text/plain",
        use_container_width=True
    )


else:

    # ========================================================
    # INITIAL SCREEN
    # ========================================================

    st.info(
        "👈 Enter the voyage parameters in the sidebar "
        "and click **Analyse Voyage** to generate the analysis."
    )


# ============================================================
# FOOTER
# ============================================================

st.divider()

st.caption(
    "🚢 Intelligent Freight Forecasting & Vessel Chartering System "
    "| Live weather powered by Open-Meteo"
)