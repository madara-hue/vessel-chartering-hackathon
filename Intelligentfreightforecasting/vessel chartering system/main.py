from modules.vessel_matching import find_suitable_vessels
from modules.procurement import find_suitable_suppliers
from modules.cost_calculation import calculate_voyage_cost

from modules.recommendation import (
    calculate_vessel_scores,
    calculate_supplier_scores
)

voyage_results = []

print("====================================================")
print("   VESSEL CHARTERING & BULK CARGO PROCUREMENT")
print("====================================================")


# ------------------------------------------
# 1. GET PROJECT INPUT
# ------------------------------------------

cargo_type = input("Enter cargo type: ").strip()

quantity_input = input(
    "Enter required cargo quantity (MT): "
)

quantity_input = quantity_input.replace(",", "")
quantity_input = quantity_input.replace("MT", "")
quantity_input = quantity_input.strip()

try:
    cargo_quantity = float(quantity_input)
except ValueError:
    print("\nInvalid cargo quantity.")
    exit()

origin = input("Enter origin port: ").strip()
destination = input("Enter destination port: ").strip()


print("\n====================================================")
print("                 PROJECT INPUT")
print("====================================================")

print(f"Cargo Type       : {cargo_type}")
print(f"Quantity         : {cargo_quantity:,.0f} MT")
print(f"Origin           : {origin}")
print(f"Destination      : {destination}")


# ------------------------------------------
# 2. FIND SUITABLE VESSELS
# ------------------------------------------

print("\n====================================================")
print("             VESSEL CHARTERING ANALYSIS")
print("====================================================")

vessels = find_suitable_vessels(
    cargo_quantity,
    origin,
    destination
)

if vessels.empty:

    print("No suitable vessels found.")

else:

    print("\nSuitable vessels:")

    vessel_columns = [
        "Vessel_ID",
        "Vessel_Name",
        "Vessel_Type",
        "DWT",
        "Speed_Knots",
        "Daily_Charter_Rate_USD"
    ]

    print(
        vessels[vessel_columns].to_string(index=False)
    )


# ------------------------------------------
# 3. FIND SUITABLE SUPPLIERS
# ------------------------------------------

print("\n====================================================")
print("             BULK CARGO PROCUREMENT")
print("====================================================")

suppliers = find_suitable_suppliers(
    cargo_type,
    cargo_quantity
)

if suppliers.empty:

    print("No suitable suppliers found.")

else:

    print("\nSuitable suppliers:")

    supplier_columns = [
        "Supplier_ID",
        "Supplier_Name",
        "Cargo_Type",
        "Price_Per_MT_USD",
        "Quality_Score",
        "Available_Quantity_MT",
        "Delivery_Reliability",
        "Estimated_Procurement_Cost_USD"
    ]

    print(
        suppliers[supplier_columns].to_string(index=False)
    )


# ------------------------------------------
# 4. CALCULATE VOYAGE COST
# ------------------------------------------

print("\n====================================================")
print("                VOYAGE COST ANALYSIS")
print("====================================================")

if vessels.empty:

    print("Voyage cost cannot be calculated because")
    print("there are no suitable vessels.")

else:

    voyage_results = []

    for _, vessel in vessels.iterrows():

        result = calculate_voyage_cost(
            vessel["Vessel_ID"],
            origin,
            destination,
            cargo_quantity
        )

        if result is not None:

            voyage_results.append(result)

print("\n====================================================")
print("              VESSEL SCORE ANALYSIS")
print("====================================================")

if len(voyage_results) == 0:
    print("No vessel scores available.")
else:
    vessel_scores = calculate_vessel_scores(voyage_results)

    for vessel in vessel_scores:
        print(
            f"{vessel['Vessel_Name']} | "
            f"Cost: ${vessel['Total_Voyage_Cost_USD']:,.2f} | "
            f"Duration: {vessel['Voyage_Days']:.2f} days | "
            f"Score: {vessel['Vessel_Score']:.2f}/100"
        )
    if not voyage_results:

        print("No voyage cost could be calculated.")

    else:

        for result in voyage_results:

            print("\n------------------------------------------")

            print(
                f"Vessel            : "
                f"{result['Vessel_Name']}"
            )

            print(
                f"Voyage Duration   : "
                f"{result['Voyage_Days']:.2f} days"
            )

            print(
                f"Fuel Consumption  : "
                f"{result['Fuel_Consumption_MT']:.2f} MT"
            )

            print(
                f"Fuel Cost         : "
                f"${result['Fuel_Cost_USD']:,.2f}"
            )

            print(
                f"Charter Cost      : "
                f"${result['Charter_Cost_USD']:,.2f}"
            )

            print(
                f"Port Cost         : "
                f"${result['Port_Cost_USD']:,.2f}"
            )

            print(
                f"Total Voyage Cost : "
                f"${result['Total_Voyage_Cost_USD']:,.2f}"
            )


# ------------------------------------------
# 5. PROCUREMENT + VOYAGE COST
# ------------------------------------------

print("\n====================================================")
print("              TOTAL PROJECT COST")
print("====================================================")

if suppliers.empty:

    print("Cannot calculate total project cost.")
    print("No suitable supplier found.")

elif not voyage_results:

    print("Cannot calculate total project cost.")
    print("No voyage cost available.")

else:

    # Lowest supplier procurement cost
    lowest_supplier_cost = suppliers.iloc[0][
        "Estimated_Procurement_Cost_USD"
    ]

    # Lowest voyage cost
    lowest_voyage_cost = min(
        result["Total_Voyage_Cost_USD"]
        for result in voyage_results
    )

    total_project_cost = (
        lowest_supplier_cost +
        lowest_voyage_cost
    )

    print(
        f"Cargo Procurement Cost : "
        f"${lowest_supplier_cost:,.2f}"
    )

    print(
        f"Voyage Cost            : "
        f"${lowest_voyage_cost:,.2f}"
    )

    print("------------------------------------------")

    print(
        f"TOTAL PROJECT COST     : "
        f"${total_project_cost:,.2f}"
    )


print("\n====================================================")
print("              ANALYSIS COMPLETED")
print("====================================================")

# STEP 7 - SUPPLIER SCORE ANALYSIS

print("\n====================================================")
print("             SUPPLIER SCORE ANALYSIS")
print("====================================================")

supplier_scores = calculate_supplier_scores(suppliers)

if supplier_scores is None or len(supplier_scores) == 0:
    print("No supplier scores available.")
else:
    for _, supplier in supplier_scores.iterrows():
        print(
            f"{supplier['Supplier_Name']} | "
            f"Price: ${supplier['Price_Per_MT_USD']:,.2f}/MT | "
            f"Quality: {supplier['Quality_Score']} | "
            f"Reliability: {supplier['Delivery_Reliability']} | "
            f"Score: {supplier['Supplier_Score']:.2f}/100"
        )


print("\n====================================================")
print("              FINAL RECOMMENDATION")
print("====================================================")

if vessel_scores and len(supplier_scores) > 0:

    best_vessel = vessel_scores[0]
    best_supplier = supplier_scores.iloc[0]

    cargo_cost = (
        best_supplier["Price_Per_MT_USD"]
        * cargo_quantity
    )

    voyage_cost = best_vessel["Total_Voyage_Cost_USD"]

    total_cost = cargo_cost + voyage_cost

    print("\nRECOMMENDED VESSEL")
    print("-----------------------------")
    print(f"Vessel Name       : {best_vessel['Vessel_Name']}")
    print(f"Voyage Duration   : {best_vessel['Voyage_Days']:.2f} days")
    print(f"Fuel Consumption  : {best_vessel['Fuel_Consumption_MT']:.2f} MT")
    print(f"Voyage Cost       : ${voyage_cost:,.2f}")
    print(f"Vessel Score      : {best_vessel['Vessel_Score']:.2f}/100")

    print("\nRECOMMENDED SUPPLIER")
    print("-----------------------------")
    print(f"Supplier Name     : {best_supplier['Supplier_Name']}")
    print(f"Price per MT      : ${best_supplier['Price_Per_MT_USD']:,.2f}")
    print(f"Quality Score     : {best_supplier['Quality_Score']}")
    print(f"Reliability       : {best_supplier['Delivery_Reliability']}")
    print(f"Supplier Score    : {best_supplier['Supplier_Score']:.2f}/100")

    print("\nCOST SUMMARY")
    print("-----------------------------")
    print(f"Cargo Procurement : ${cargo_cost:,.2f}")
    print(f"Voyage Cost       : ${voyage_cost:,.2f}")
    print(f"TOTAL PROJECT COST: ${total_cost:,.2f}")

else:

    print("Final recommendation cannot be generated.")