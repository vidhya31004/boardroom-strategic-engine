import pandas as pd
from scipy.optimize import minimize_scalar

# Load dataset
df = pd.read_csv("data/product_master.csv")


# -----------------------------
# DEMAND FUNCTION
# -----------------------------
def calculate_demand(base_demand, base_price, new_price, elasticity):

    demand = base_demand * ((new_price / base_price) ** elasticity)

    return max(0, round(demand))


# -----------------------------
# METRICS ENGINE
# -----------------------------
def forecast_metrics(row, price):

    demand = calculate_demand(
        row["base_demand"],
        row["base_price"],
        price,
        row["elasticity"]
    )

    demand = min(demand, row["max_capacity"])

    revenue = demand * price
    cost = demand * row["unit_cost"]
    profit = revenue - cost
    margin = profit / revenue if revenue > 0 else 0

    return {
        "product": row["product"],
        "optimal_price": round(price, 2),
        "demand": demand,
        "revenue": round(revenue, 2),
        "profit": round(profit, 2),
        "margin": round(margin, 2)
    }


# -----------------------------
# PROFIT FUNCTION
# -----------------------------
def profit_function(price, row):

    demand = calculate_demand(
        row["base_demand"],
        row["base_price"],
        price,
        row["elasticity"]
    )

    demand = min(demand, row["max_capacity"])

    revenue = demand * price
    cost = demand * row["unit_cost"]

    return -(revenue - cost)  # scipy minimizes


# -----------------------------
# FIND OPTIMAL PRICE
# -----------------------------
def find_optimal_price(row):

    result = minimize_scalar(
        profit_function,
        bounds=(row["unit_cost"], row["base_price"] * 3),
        args=(row,),
        method='bounded'
    )

    optimal_price = result.x

    return forecast_metrics(row, optimal_price)


# -----------------------------
# EXECUTIVE STRATEGY LAYER
# -----------------------------
def strategy_recommendation(optimal_df):

    print("\n===== EXECUTIVE RECOMMENDATION =====\n")

    top_product = optimal_df.sort_values(
        by="profit", ascending=False
    ).iloc[0]

    print(f"""
Focus on maximizing sales of {top_product['product']}.

Optimal Price: ${top_product['optimal_price']}
Expected Profit: ${round(top_product['profit'],2)}

This product delivers the strongest profit contribution
under current demand conditions.
""")


# -----------------------------
# RUN BOARDROOM ENGINE
# -----------------------------
def run_boardroom_engine():

    optimal_results = []

    for _, row in df.iterrows():
        optimal_results.append(find_optimal_price(row))

    optimal_df = pd.DataFrame(optimal_results)

    print("\n===== BOARDROOM PRICING STRATEGY =====\n")
    print(optimal_df)

    print("\n===== COMPANY SUMMARY =====\n")

    total_revenue = optimal_df["revenue"].sum()
    total_profit = optimal_df["profit"].sum()
    margin = total_profit / total_revenue

    print("Total Revenue:", round(total_revenue, 2))
    print("Total Profit:", round(total_profit, 2))
    print("Overall Margin:", round(margin, 2))

    strategy_recommendation(optimal_df)


# Run engine
run_boardroom_engine()
