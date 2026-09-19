import pandas as pd


def find_suitable_suppliers(cargo_type, quantity):

    suppliers = pd.read_csv("data/suppliers.csv")

    # Match cargo type
    suitable_suppliers = suppliers[
        suppliers["Cargo_Type"].str.lower() == cargo_type.lower()
    ].copy()

    # Check available quantity
    suitable_suppliers = suitable_suppliers[
        suitable_suppliers["Available_Quantity_MT"] >= quantity
    ].copy()

    # Calculate estimated procurement cost
    suitable_suppliers["Estimated_Procurement_Cost_USD"] = (
        suitable_suppliers["Price_Per_MT_USD"] * quantity
    )

    # Sort by price
    suitable_suppliers = suitable_suppliers.sort_values(
        by="Price_Per_MT_USD"
    )

    return suitable_suppliers