import pandas as pd


def calculate_voyage_cost(
    vessel_id,
    origin,
    destination,
    cargo_quantity
):

    vessels = pd.read_csv("data/vessels.csv")
    freight = pd.read_csv("data/freight_rates.csv")

    # Convert numeric columns to numbers
    numeric_columns = [
        "DWT",
        "Speed_Knots",
        "Daily_Charter_Rate_USD",
        "Fuel_Consumption_MT_Day"
    ]

    for column in numeric_columns:
        vessels[column] = pd.to_numeric(
            vessels[column],
            errors="coerce"
        )

    freight_columns = [
        "Distance_NM",
        "Fuel_Price_USD_MT",
        "Port_Cost_USD"
    ]

    for column in freight_columns:
        freight[column] = pd.to_numeric(
            freight[column],
            errors="coerce"
        )

    # Find vessel
    vessel = vessels[
        vessels["Vessel_ID"].astype(str).str.strip()
        == str(vessel_id).strip()
    ]

    if vessel.empty:
        return None

    vessel = vessel.iloc[0]

    # Find route
    route = freight[
        (freight["Origin"].astype(str).str.strip().str.lower()
         == origin.strip().lower()) &
        (freight["Destination"].astype(str).str.strip().str.lower()
         == destination.strip().lower())
    ]

    if route.empty:
        return None

    route = route.iloc[0]

    # Get values
    speed = float(vessel["Speed_Knots"])
    daily_rate = float(vessel["Daily_Charter_Rate_USD"])
    fuel_consumption = float(
        vessel["Fuel_Consumption_MT_Day"]
    )

    distance = float(route["Distance_NM"])
    fuel_price = float(route["Fuel_Price_USD_MT"])
    port_cost = float(route["Port_Cost_USD"])

    # Calculations
    voyage_days = distance / (speed * 24)

    total_fuel = voyage_days * fuel_consumption

    fuel_cost = total_fuel * fuel_price

    charter_cost = voyage_days * daily_rate

    total_voyage_cost = (
        fuel_cost +
        charter_cost +
        port_cost
    )

    return {
        "Vessel_Name": vessel["Vessel_Name"],
        "Distance_NM": distance,
        "Voyage_Days": voyage_days,
        "Fuel_Consumption_MT": total_fuel,
        "Fuel_Cost_USD": fuel_cost,
        "Charter_Cost_USD": charter_cost,
        "Port_Cost_USD": port_cost,
        "Total_Voyage_Cost_USD": total_voyage_cost
    }