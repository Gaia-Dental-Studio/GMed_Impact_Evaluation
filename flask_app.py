from flask import Flask, request, jsonify
import pandas as pd
import json
import numpy as np
from model import Model

app = Flask(__name__)

# Load configuration
with open("parameters.json") as f:
    CONFIG = json.load(f)

# Load data
prevalence_data = pd.read_csv("indonesia_ncd_prevalence_cleaned.csv", index_col=0)
economic_burden_undiagnosed_data = pd.read_csv("indonesia_ncd_economic_burden_undiagnosed_cleaned.csv", index_col=0)
provinces_data = pd.read_csv("provinces_population.csv")
provinces_data["Population"] = provinces_data["Population"].fillna("0").str.replace('"', '', regex=False).str.replace(",", "", regex=False).astype(int)

# Model instance (only for pictogram use later if extended)
model = Model()

@app.route("/predict", methods=["POST"])
def predict():
    data = request.json

    disease = data["disease"]
    province = data["province"]
    year = int(data["year"])
    clinics = int(data["clinics"])
    providers = int(data["providers"])
    capacity_pct = float(data["capacity_pct"])

    # Config values
    old_ratio = CONFIG["old_ratio"]
    old_population_all = CONFIG["old_population_all"]
    growth_rate = CONFIG["growth_rate"]
    capacity_yearly = CONFIG["capacity_yearly"]
    undiagnosed_ratio = CONFIG["undiagnosed_ratio"][disease]

    # Population
    if province == "Indonesia (All Provinces)":
        old_population = old_population_all
    else:
        old_population = provinces_data[provinces_data["Province"] == province]["Population"].values[0] * old_ratio

    # Compute projected population
    projected_pop = old_population * (1 + growth_rate * (year - 2024))
    prevalence_pct = prevalence_data[disease].loc[year]
    susceptible_population = projected_pop * prevalence_pct / 100

    # National baseline
    projected_pop_all = old_population_all * (1 + growth_rate * (year - 2024))
    susceptible_all = projected_pop_all * prevalence_pct / 100

    # Economic burden
    burden_unit_cost = economic_burden_undiagnosed_data[disease].loc[year]
    economic_burden = burden_unit_cost * (susceptible_population / susceptible_all)

    # Split population
    diagnosed = susceptible_population * (1 - undiagnosed_ratio)
    undiagnosed = susceptible_population * undiagnosed_ratio
    econ_burden_per_capita = economic_burden / undiagnosed if undiagnosed > 0 else 0

    # Intervention calculation
    intervention_capacity = capacity_yearly * clinics * providers * capacity_pct / 100 / 20
    pct_undiag_before = undiagnosed_ratio * 100
    pct_undiag_after = max(0, pct_undiag_before * (1 - (intervention_capacity / undiagnosed))) if undiagnosed > 0 else 0

    economic_burden_after = max(0, economic_burden * (1 - intervention_capacity / undiagnosed)) if undiagnosed > 0 else 0
    economic_burden_delta = economic_burden - economic_burden_after

    return jsonify({
        "population": round(projected_pop),
        "susceptible_population": round(susceptible_population),
        "susceptible_diagnosed": round(diagnosed),
        "susceptible_undiagnosed": round(undiagnosed),
        "economic_burden": round(economic_burden),
        "economic_burden_per_capita": round(econ_burden_per_capita),
        "intervention_capacity": round(intervention_capacity),
        "pct_undiag_before": round(pct_undiag_before, 2),
        "pct_undiag_after": round(pct_undiag_after, 2),
        "economic_burden_after": round(economic_burden_after),
        "economic_burden_delta": round(economic_burden_delta)
    })


if __name__ == "__main__":
    app.run(debug=True)
