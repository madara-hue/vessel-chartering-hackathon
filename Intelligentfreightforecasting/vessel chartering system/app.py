import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd

from modules.cost_calculation import calculate_voyage_cost
from modules.recommendation import (
    calculate_vessel_scores,
    calculate_supplier_scores
)

from modules.weather_analysis import (
    get_weather_data,
    calculate_weather_score
)


# ============================================================
# LOAD DATASETS
# ============================================================

try:
    vessels = pd.read_csv("data/vessels.csv")
    suppliers = pd.read_csv("data/suppliers.csv")
    ports = pd.read_csv("data/ports.csv")
    freight_rates = pd.read_csv("data/freight_rates.csv")
    weather = pd.read_csv("data/weather.csv")
    congestion = pd.read_csv("data/port_congestion.csv")

except Exception as error:
    print("Error loading datasets:", error)
    raise


# ============================================================
# CONGESTION FUNCTIONS
# ============================================================

def get_congestion_data(port_name):

    result = congestion[
        congestion["Port_Name"].astype(str).str.lower()
        == port_name.lower()
    ]

    if result.empty:
        return None

    return result.iloc[0]


def calculate_congestion_score(congestion_data):

    if congestion_data is None:
        return 0

    level = str(
        congestion_data["Congestion_Level"]
    ).lower()

    if level == "low":
        return 90

    elif level == "medium":
        return 70

    elif level == "high":
        return 45

    else:
        return 50


# ============================================================
# MAIN CALCULATION
# ============================================================

def calculate():

    # --------------------------------------------------------
    # GET INPUT
    # --------------------------------------------------------

    cargo_type = cargo_var.get().strip()
    quantity_text = quantity_entry.get().strip()
    origin = origin_var.get().strip()
    destination = destination_var.get().strip()

    output_box.delete("1.0", tk.END)

    # --------------------------------------------------------
    # VALIDATION
    # --------------------------------------------------------

    if not cargo_type:

        messagebox.showerror(
            "Missing Cargo",
            "Please select a cargo type."
        )

        return

    try:

        quantity = float(quantity_text)

    except ValueError:

        messagebox.showerror(
            "Invalid Quantity",
            "Please enter a valid number."
        )

        return

    if quantity <= 0:

        messagebox.showerror(
            "Invalid Quantity",
            "Quantity must be greater than zero."
        )

        return

    if not origin or not destination:

        messagebox.showerror(
            "Missing Port",
            "Please select both ports."
        )

        return

    if origin.lower() == destination.lower():

        messagebox.showerror(
            "Invalid Route",
            "Origin and destination cannot be the same."
        )

        return


    # ========================================================
    # HEADER
    # ========================================================

    output_box.insert(
        tk.END,
        "============================================================\n"
        "       VESSEL CHARTERING & BULK CARGO PROCUREMENT\n"
        "============================================================\n\n"
    )

    output_box.insert(
        tk.END,
        f"Cargo Type       : {cargo_type}\n"
        f"Cargo Quantity   : {quantity:,.0f} MT\n"
        f"Origin Port      : {origin}\n"
        f"Destination Port : {destination}\n\n"
    )


    # ========================================================
    # SUPPLIER MATCHING
    # ========================================================

    suitable_suppliers = suppliers[
        (
            suppliers["Cargo_Type"]
            .astype(str)
            .str.lower()
            == cargo_type.lower()
        )
        &
        (
            pd.to_numeric(
                suppliers["Available_Quantity_MT"],
                errors="coerce"
            )
            >= quantity
        )
    ].copy()


    output_box.insert(
        tk.END,
        "SUPPLIER ANALYSIS\n"
        "------------------------------------------------------------\n"
    )


    if suitable_suppliers.empty:

        output_box.insert(
            tk.END,
            "No suitable supplier found.\n\n"
        )

        supplier_scores = pd.DataFrame()

    else:

        output_box.insert(
            tk.END,
            f"Suitable suppliers found: "
            f"{len(suitable_suppliers)}\n\n"
        )

        for _, supplier in suitable_suppliers.iterrows():

            output_box.insert(
                tk.END,
                f"Supplier: "
                f"{supplier['Supplier_Name']}\n"
                f"Price: "
                f"${float(supplier['Price_Per_MT_USD']):,.2f}/MT\n"
                f"Quality: "
                f"{supplier['Quality_Score']}\n"
                f"Reliability: "
                f"{supplier['Delivery_Reliability']}\n"
                "------------------------------------------------------------\n"
            )

        try:

            supplier_scores = calculate_supplier_scores(
                suitable_suppliers
            )

        except Exception as error:

            print(
                "Supplier scoring error:",
                error
            )

            supplier_scores = pd.DataFrame()


    # ========================================================
    # VESSEL MATCHING
    # ========================================================

    suitable_vessels = vessels[
        pd.to_numeric(
            vessels["DWT"],
            errors="coerce"
        ) >= quantity
    ].copy()


    output_box.insert(
        tk.END,
        "\nVESSEL ANALYSIS\n"
        "------------------------------------------------------------\n"
    )


    if suitable_vessels.empty:

        output_box.insert(
            tk.END,
            "No suitable vessel found.\n\n"
        )

        vessel_scores = []
        voyage_results = []

    else:

        output_box.insert(
            tk.END,
            f"Suitable vessels found: "
            f"{len(suitable_vessels)}\n\n"
        )

        for _, vessel in suitable_vessels.iterrows():

            output_box.insert(
                tk.END,
                f"Vessel: "
                f"{vessel['Vessel_Name']}\n"
                f"DWT: "
                f"{float(vessel['DWT']):,.0f} MT\n"
                f"Speed: "
                f"{vessel['Speed_Knots']} knots\n"
                f"Charter Rate: "
                f"${float(vessel['Daily_Charter_Rate_USD']):,.2f}/day\n"
                "------------------------------------------------------------\n"
            )


        # ----------------------------------------------------
        # ROUTE
        # ----------------------------------------------------

        route = freight_rates[
            (
                freight_rates["Origin"]
                .astype(str)
                .str.lower()
                == origin.lower()
            )
            &
            (
                freight_rates["Destination"]
                .astype(str)
                .str.lower()
                == destination.lower()
            )
        ].copy()


        if route.empty:

            route_data = None

        else:

            route_data = route.iloc[0]


        # ----------------------------------------------------
        # VOYAGE COST
        # ----------------------------------------------------

        voyage_results = []


        if route_data is not None:

            for _, vessel in suitable_vessels.iterrows():

                try:

                    result = calculate_voyage_cost(
                        vessel["Vessel_ID"],
                        origin,
                        destination,
                        quantity
                    )

                    if result is not None:

                        voyage_results.append(result)

                except Exception as error:

                    print(
                        "Voyage calculation error:",
                        error
                    )


        # ----------------------------------------------------
        # VESSEL SCORING
        # ----------------------------------------------------

        if voyage_results:

            try:

                vessel_scores = calculate_vessel_scores(
                    voyage_results
                )

            except Exception as error:

                print(
                    "Vessel scoring error:",
                    error
                )

                vessel_scores = []

        else:

            vessel_scores = []


    # ========================================================
    # ROUTE INFORMATION
    # ========================================================

    output_box.insert(
        tk.END,
        "\nROUTE INFORMATION\n"
        "------------------------------------------------------------\n"
    )


    if route_data is None:

        output_box.insert(
            tk.END,
            "No route found in freight-rate dataset.\n"
        )

    else:

        output_box.insert(
            tk.END,
            f"Route       : {origin} → {destination}\n"
            f"Distance    : "
            f"{route_data['Distance_NM']} NM\n"
            f"Fuel Price  : "
            f"${route_data['Fuel_Price_USD_MT']}/MT\n"
            f"Port Cost   : "
            f"${route_data['Port_Cost_USD']:,.2f}\n"
        )


    # ========================================================
    # WEATHER ANALYSIS
    # ========================================================

    origin_weather = get_weather_data(
        "data/weather.csv",
        origin
    )

    destination_weather = get_weather_data(
        "data/weather.csv",
        destination
    )


    origin_weather_score = calculate_weather_score(
        origin_weather
    )

    destination_weather_score = calculate_weather_score(
        destination_weather
    )


    if (
        origin_weather is not None
        and destination_weather is not None
    ):

        overall_weather_score = (
            origin_weather_score
            + destination_weather_score
        ) / 2

    elif origin_weather is not None:

        overall_weather_score = origin_weather_score

    elif destination_weather is not None:

        overall_weather_score = destination_weather_score

    else:

        overall_weather_score = 0


    output_box.insert(
        tk.END,
        "\nWEATHER ANALYSIS\n"
        "------------------------------------------------------------\n"
    )


    if origin_weather is not None:

        output_box.insert(
            tk.END,
            f"{origin}: "
            f"{origin_weather['Weather_Condition']}\n"
            f"Wind: "
            f"{origin_weather['Wind_Speed_Knots']} knots\n"
            f"Wave: "
            f"{origin_weather['Wave_Height_M']} m\n"
            f"Visibility: "
            f"{origin_weather['Visibility_KM']} km\n"
            f"Weather Score: "
            f"{origin_weather_score:.2f}/100\n\n"
        )


    if destination_weather is not None:

        output_box.insert(
            tk.END,
            f"{destination}: "
            f"{destination_weather['Weather_Condition']}\n"
            f"Wind: "
            f"{destination_weather['Wind_Speed_Knots']} knots\n"
            f"Wave: "
            f"{destination_weather['Wave_Height_M']} m\n"
            f"Visibility: "
            f"{destination_weather['Visibility_KM']} km\n"
            f"Weather Score: "
            f"{destination_weather_score:.2f}/100\n\n"
        )


    output_box.insert(
        tk.END,
        f"Overall Weather Score: "
        f"{overall_weather_score:.2f}/100\n"
    )


    # ========================================================
    # PORT CONGESTION
    # ========================================================

    origin_congestion = get_congestion_data(
        origin
    )

    destination_congestion = get_congestion_data(
        destination
    )


    origin_congestion_score = calculate_congestion_score(
        origin_congestion
    )

    destination_congestion_score = calculate_congestion_score(
        destination_congestion
    )


    if (
        origin_congestion is not None
        and destination_congestion is not None
    ):

        total_waiting_hours = (
            float(
                origin_congestion[
                    "Average_Waiting_Hours"
                ]
            )
            +
            float(
                destination_congestion[
                    "Average_Waiting_Hours"
                ]
            )
        )

        overall_congestion_score = (
            origin_congestion_score
            + destination_congestion_score
        ) / 2

    elif origin_congestion is not None:

        total_waiting_hours = float(
            origin_congestion[
                "Average_Waiting_Hours"
            ]
        )

        overall_congestion_score = (
            origin_congestion_score
        )

    elif destination_congestion is not None:

        total_waiting_hours = float(
            destination_congestion[
                "Average_Waiting_Hours"
            ]
        )

        overall_congestion_score = (
            destination_congestion_score
        )

    else:

        total_waiting_hours = 0
        overall_congestion_score = 0


    output_box.insert(
        tk.END,
        "\nPORT CONGESTION ANALYSIS\n"
        "------------------------------------------------------------\n"
    )


    if origin_congestion is not None:

        output_box.insert(
            tk.END,
            f"{origin}:\n"
            f"Congestion: "
            f"{origin_congestion['Congestion_Level']}\n"
            f"Waiting Time: "
            f"{origin_congestion['Average_Waiting_Hours']} hours\n"
            f"Berth Availability: "
            f"{origin_congestion['Berth_Availability']}%\n\n"
        )


    if destination_congestion is not None:

        output_box.insert(
            tk.END,
            f"{destination}:\n"
            f"Congestion: "
            f"{destination_congestion['Congestion_Level']}\n"
            f"Waiting Time: "
            f"{destination_congestion['Average_Waiting_Hours']} hours\n"
            f"Berth Availability: "
            f"{destination_congestion['Berth_Availability']}%\n\n"
        )


    output_box.insert(
        tk.END,
        f"Total Estimated Waiting Time: "
        f"{total_waiting_hours:.1f} hours\n"
        f"Congestion Score: "
        f"{overall_congestion_score:.2f}/100\n"
    )


    # ========================================================
    # VOYAGE COST RESULTS
    # ========================================================

    output_box.insert(
        tk.END,
        "\nVOYAGE COST ANALYSIS\n"
        "------------------------------------------------------------\n"
    )


    if not voyage_results:

        output_box.insert(
            tk.END,
            "No voyage cost could be calculated.\n"
        )

    else:

        for result in voyage_results:

            output_box.insert(
                tk.END,
                f"Vessel: "
                f"{result.get('Vessel_Name', 'Unknown')}\n"
                f"Voyage Days: "
                f"{float(result.get('Voyage_Days', 0)):.2f}\n"
                f"Fuel Consumption: "
                f"{float(result.get('Fuel_Consumption_MT', 0)):.2f} MT\n"
                f"Fuel Cost: "
                f"${float(result.get('Fuel_Cost_USD', 0)):,.2f}\n"
                f"Charter Cost: "
                f"${float(result.get('Charter_Cost_USD', 0)):,.2f}\n"
                f"Port Cost: "
                f"${float(result.get('Port_Cost_USD', 0)):,.2f}\n"
                f"Total Voyage Cost: "
                f"${float(result.get('Total_Voyage_Cost_USD', 0)):,.2f}\n"
                "------------------------------------------------------------\n"
            )


    # ========================================================
    # VESSEL SCORES
    # ========================================================

    output_box.insert(
        tk.END,
        "\nVESSEL SCORE ANALYSIS\n"
        "------------------------------------------------------------\n"
    )


    if vessel_scores:

        for vessel in vessel_scores:

            output_box.insert(
                tk.END,
                f"{vessel.get('Vessel_Name', 'Unknown')} | "
                f"Score: "
                f"{float(vessel.get('Vessel_Score', 0)):.2f}/100\n"
            )

    else:

        output_box.insert(
            tk.END,
            "No vessel scores available.\n"
        )


    # ========================================================
    # SUPPLIER SCORES
    # ========================================================

    output_box.insert(
        tk.END,
        "\nSUPPLIER SCORE ANALYSIS\n"
        "------------------------------------------------------------\n"
    )


    if (
        supplier_scores is not None
        and len(supplier_scores) > 0
    ):

        for _, supplier in supplier_scores.iterrows():

            output_box.insert(
                tk.END,
                f"{supplier['Supplier_Name']} | "
                f"Score: "
                f"{float(supplier['Supplier_Score']):.2f}/100\n"
            )

    else:

        output_box.insert(
            tk.END,
            "No supplier scores available.\n"
        )


    # ========================================================
    # DECISION SUMMARY
    # ========================================================

    if (
        vessel_scores
        and supplier_scores is not None
        and len(supplier_scores) > 0
    ):

        best_vessel = vessel_scores[0]

        best_supplier = supplier_scores.iloc[0]


        vessel_name = best_vessel.get(
            "Vessel_Name",
            "Unknown"
        )

        vessel_score = float(
            best_vessel.get(
                "Vessel_Score",
                0
            )
        )


        supplier_name = best_supplier[
            "Supplier_Name"
        ]

        supplier_score = float(
            best_supplier[
                "Supplier_Score"
            ]
        )


        supplier_price = float(
            best_supplier[
                "Price_Per_MT_USD"
            ]
        )


        voyage_cost = float(
            best_vessel.get(
                "Total_Voyage_Cost_USD",
                0
            )
        )


        procurement_cost = (
            supplier_price * quantity
        )


        # ----------------------------------------------------
        # ESTIMATED WAITING COST
        # ----------------------------------------------------

        daily_charter_rate = 0

        for _, vessel in suitable_vessels.iterrows():

            if (
                vessel["Vessel_Name"]
                == vessel_name
            ):

                daily_charter_rate = float(
                    vessel[
                        "Daily_Charter_Rate_USD"
                    ]
                )

                break


        waiting_days = (
            total_waiting_hours / 24
        )


        estimated_waiting_cost = (
            waiting_days
            * daily_charter_rate
        )


        total_project_cost = (
            procurement_cost
            + voyage_cost
            + estimated_waiting_cost
        )


        # ----------------------------------------------------
        # UPDATE DECISION SUMMARY
        # ----------------------------------------------------

        origin_condition = (
            origin_weather[
                "Weather_Condition"
            ]
            if origin_weather is not None
            else "No data"
        )


        destination_condition = (
            destination_weather[
                "Weather_Condition"
            ]
            if destination_weather is not None
            else "No data"
        )


        origin_congestion_level = (
            origin_congestion[
                "Congestion_Level"
            ]
            if origin_congestion is not None
            else "No data"
        )


        destination_congestion_level = (
            destination_congestion[
                "Congestion_Level"
            ]
            if destination_congestion is not None
            else "No data"
        )


        summary_label.config(
            text=
            f"RECOMMENDED VESSEL\n"
            f"{vessel_name} | Score: "
            f"{vessel_score:.2f}/100\n\n"

            f"RECOMMENDED SUPPLIER\n"
            f"{supplier_name} | Score: "
            f"{supplier_score:.2f}/100\n\n"

            f"WEATHER ANALYSIS\n"
            f"{origin}: {origin_condition} | "
            f"Score: {origin_weather_score:.2f}/100\n"
            f"{destination}: {destination_condition} | "
            f"Score: {destination_weather_score:.2f}/100\n"
            f"Overall Weather Score: "
            f"{overall_weather_score:.2f}/100\n\n"

            f"PORT CONGESTION\n"
            f"{origin}: {origin_congestion_level}\n"
            f"{destination}: {destination_congestion_level}\n"
            f"Estimated Waiting Time: "
            f"{total_waiting_hours:.1f} hours\n"
            f"Congestion Score: "
            f"{overall_congestion_score:.2f}/100\n\n"

            f"COST SUMMARY\n"
            f"Cargo Procurement: "
            f"${procurement_cost:,.2f}\n"
            f"Voyage Cost: "
            f"${voyage_cost:,.2f}\n"
            f"Estimated Waiting Cost: "
            f"${estimated_waiting_cost:,.2f}\n"
            f"TOTAL PROJECT COST: "
            f"${total_project_cost:,.2f}"
        )


        # ----------------------------------------------------
        # FINAL RECOMMENDATION
        # ----------------------------------------------------

        output_box.insert(
            tk.END,
            "\n\nFINAL RECOMMENDATION\n"
            "============================================================\n"
            f"Recommended Vessel : {vessel_name}\n"
            f"Vessel Score       : {vessel_score:.2f}/100\n\n"
            f"Recommended Supplier: {supplier_name}\n"
            f"Supplier Score      : {supplier_score:.2f}/100\n\n"
            f"Weather Score       : "
            f"{overall_weather_score:.2f}/100\n"
            f"Congestion Score    : "
            f"{overall_congestion_score:.2f}/100\n"
            f"Waiting Time        : "
            f"{total_waiting_hours:.1f} hours\n\n"
            f"Cargo Cost          : "
            f"${procurement_cost:,.2f}\n"
            f"Voyage Cost         : "
            f"${voyage_cost:,.2f}\n"
            f"Waiting Cost        : "
            f"${estimated_waiting_cost:,.2f}\n"
            f"TOTAL PROJECT COST  : "
            f"${total_project_cost:,.2f}\n"
            "============================================================\n"
        )

    else:

        summary_label.config(
            text=
            "No complete recommendation available.\n"
            "Check vessel, supplier and route data."
        )


# ============================================================
# CLEAR FUNCTION
# ============================================================

def clear_results():

    quantity_entry.delete(
        0,
        tk.END
    )

    output_box.delete(
        "1.0",
        tk.END
    )

    summary_label.config(
        text="Enter cargo details and click CALCULATE."
    )

    if cargo_types:
        cargo_dropdown.current(0)

    if port_names:
        origin_dropdown.current(0)

    if len(port_names) > 1:
        destination_dropdown.current(1)


# ============================================================
# GUI
# ============================================================

root = tk.Tk()

root.title(
    "Vessel Chartering & Bulk Cargo Procurement System"
)

root.geometry(
    "1050x800"
)


# ============================================================
# TITLE
# ============================================================

title_label = tk.Label(
    root,
    text="VESSEL CHARTERING & BULK CARGO PROCUREMENT",
    font=("Arial", 20, "bold")
)

title_label.pack(
    pady=(15, 5)
)


subtitle_label = tk.Label(
    root,
    text="India East Coast Shipping Decision Support System",
    font=("Arial", 11)
)

subtitle_label.pack(
    pady=(0, 15)
)


# ============================================================
# INPUT FRAME
# ============================================================

input_frame = tk.Frame(root)

input_frame.pack(
    pady=10
)


# ============================================================
# CARGO
# ============================================================

tk.Label(
    input_frame,
    text="Cargo Type:",
    font=("Arial", 11)
).grid(
    row=0,
    column=0,
    padx=10,
    pady=8,
    sticky="e"
)


cargo_types = sorted(
    suppliers["Cargo_Type"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


cargo_var = tk.StringVar()


cargo_dropdown = ttk.Combobox(
    input_frame,
    textvariable=cargo_var,
    values=cargo_types,
    state="readonly",
    width=27
)

cargo_dropdown.grid(
    row=0,
    column=1,
    padx=10,
    pady=8
)


if cargo_types:

    cargo_dropdown.current(0)


# ============================================================
# QUANTITY
# ============================================================

tk.Label(
    input_frame,
    text="Quantity (MT):",
    font=("Arial", 11)
).grid(
    row=1,
    column=0,
    padx=10,
    pady=8,
    sticky="e"
)


quantity_entry = tk.Entry(
    input_frame,
    width=30
)

quantity_entry.grid(
    row=1,
    column=1,
    padx=10,
    pady=8
)


# ============================================================
# PORTS
# ============================================================

port_names = sorted(
    ports["Port_Name"]
    .dropna()
    .astype(str)
    .unique()
    .tolist()
)


# ============================================================
# ORIGIN
# ============================================================

tk.Label(
    input_frame,
    text="Origin Port:",
    font=("Arial", 11)
).grid(
    row=2,
    column=0,
    padx=10,
    pady=8,
    sticky="e"
)


origin_var = tk.StringVar()


origin_dropdown = ttk.Combobox(
    input_frame,
    textvariable=origin_var,
    values=port_names,
    state="readonly",
    width=27
)

origin_dropdown.grid(
    row=2,
    column=1,
    padx=10,
    pady=8
)


if port_names:

    origin_dropdown.current(0)


# ============================================================
# DESTINATION
# ============================================================

tk.Label(
    input_frame,
    text="Destination Port:",
    font=("Arial", 11)
).grid(
    row=3,
    column=0,
    padx=10,
    pady=8,
    sticky="e"
)


destination_var = tk.StringVar()


destination_dropdown = ttk.Combobox(
    input_frame,
    textvariable=destination_var,
    values=port_names,
    state="readonly",
    width=27
)

destination_dropdown.grid(
    row=3,
    column=1,
    padx=10,
    pady=8
)


if len(port_names) > 1:

    destination_dropdown.current(1)


# ============================================================
# BUTTONS
# ============================================================

button_frame = tk.Frame(root)

button_frame.pack(
    pady=10
)


calculate_button = tk.Button(
    button_frame,
    text="CALCULATE",
    command=calculate,
    font=("Arial", 12, "bold"),
    padx=30,
    pady=8
)

calculate_button.grid(
    row=0,
    column=0,
    padx=10
)


clear_button = tk.Button(
    button_frame,
    text="CLEAR",
    command=clear_results,
    font=("Arial", 12),
    padx=30,
    pady=8
)

clear_button.grid(
    row=0,
    column=1,
    padx=10
)


# ============================================================
# DECISION SUMMARY
# ============================================================

summary_frame = tk.LabelFrame(
    root,
    text="Decision Summary",
    font=("Arial", 12, "bold"),
    padx=15,
    pady=10
)

summary_frame.pack(
    fill="x",
    padx=20,
    pady=5
)


summary_label = tk.Label(
    summary_frame,
    text="Enter cargo details and click CALCULATE.",
    font=("Arial", 10),
    justify="left",
    anchor="w"
)

summary_label.pack(
    fill="x"
)


# ============================================================
# OUTPUT
# ============================================================

output_frame = tk.Frame(root)

output_frame.pack(
    fill="both",
    expand=True,
    padx=20,
    pady=10
)


scrollbar = tk.Scrollbar(
    output_frame
)

scrollbar.pack(
    side="right",
    fill="y"
)


output_box = tk.Text(
    output_frame,
    height=25,
    width=115,
    font=("Consolas", 10),
    yscrollcommand=scrollbar.set
)

output_box.pack(
    side="left",
    fill="both",
    expand=True
)


scrollbar.config(
    command=output_box.yview
)


# ============================================================
# START
# ============================================================

root.mainloop()