import pandas as pd


def find_suitable_vessels(
    cargo_quantity,
    origin,
    destination
):

    vessels = pd.read_csv("data/vessels.csv")
    ports = pd.read_csv("data/ports.csv")

    # Convert vessel numeric columns
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

    # Find origin port
    origin_port = ports[
        ports["Port_Name"].astype(str).str.strip().str.lower()
        == origin.strip().lower()
    ]

    # Find destination port
    destination_port = ports[
        ports["Port_Name"].astype(str).str.strip().str.lower()
        == destination.strip().lower()
    ]

    # Check whether ports exist
    if origin_port.empty or destination_port.empty:
        return pd.DataFrame()

    origin_draft = float(
        origin_port.iloc[0]["Max_Draft_Meters"]
    )

    destination_draft = float(
        destination_port.iloc[0]["Max_Draft_Meters"]
    )

    # Simplified educational draft estimate
    vessels["Estimated_Draft"] = (
        (vessels["DWT"] / 10000) * 1.5
    ) + 5

    # Find suitable vessels
    suitable_vessels = vessels[
        (vessels["DWT"] >= cargo_quantity) &
        (vessels["Estimated_Draft"] <= origin_draft) &
        (vessels["Estimated_Draft"] <= destination_draft)
    ].copy()

    # Sort by daily charter rate
    suitable_vessels = suitable_vessels.sort_values(
        by="Daily_Charter_Rate_USD"
    )

    return suitable_vessels