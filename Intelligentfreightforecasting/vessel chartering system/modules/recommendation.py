def calculate_vessel_scores(voyage_results):
    """
    Calculates a score for each suitable vessel.

    Factors:
    - Voyage cost: 50%
    - Fuel consumption: 30%
    - Voyage duration: 20%
    """

    if not voyage_results:
        return []

    max_cost = max(
        result["Total_Voyage_Cost_USD"]
        for result in voyage_results
    )

    max_fuel = max(
        result["Fuel_Consumption_MT"]
        for result in voyage_results
    )

    max_duration = max(
        result["Voyage_Days"]
        for result in voyage_results
    )

    scored_vessels = []

    for result in voyage_results:

        cost_score = (
            max_cost / result["Total_Voyage_Cost_USD"]
        ) * 100

        fuel_score = (
            max_fuel / result["Fuel_Consumption_MT"]
        ) * 100

        duration_score = (
            max_duration / result["Voyage_Days"]
        ) * 100

        overall_score = (
            cost_score * 0.50
            + fuel_score * 0.30
            + duration_score * 0.20
        )

        new_result = result.copy()

        new_result["Vessel_Score"] = overall_score

        scored_vessels.append(new_result)

    scored_vessels.sort(
        key=lambda x: x["Vessel_Score"],
        reverse=True
    )

    return scored_vessels


def calculate_supplier_scores(suppliers):

    """
    Calculates supplier scores.

    Factors:
    - Price: 50%
    - Quality: 25%
    - Delivery reliability: 25%
    """

    if suppliers is None or len(suppliers) == 0:
        return suppliers

    df = suppliers.copy()

    max_price = df["Price_Per_MT_USD"].max()
    max_quality = df["Quality_Score"].max()
    max_reliability = df["Delivery_Reliability"].max()

    df["Price_Score"] = (
        max_price / df["Price_Per_MT_USD"]
    ) * 100

    df["Quality_Normalized"] = (
        df["Quality_Score"] / max_quality
    ) * 100

    df["Reliability_Score"] = (
        df["Delivery_Reliability"] / max_reliability
    ) * 100

    df["Supplier_Score"] = (
        df["Price_Score"] * 0.50
        + df["Quality_Normalized"] * 0.25
        + df["Reliability_Score"] * 0.25
    )

    return df.sort_values(
        by="Supplier_Score",
        ascending=False
    )