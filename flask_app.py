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

# Load data worldwide

world_data = pd.read_csv('world_data_cleaned_new.csv')

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


@app.route("/predict_worldwide", methods=["POST"])
def predict_worldwide():
    data = request.json

    default_year = 2024  # <-- Add this line

    selected_country = data["country"]
    selected_disease = data["disease"]
    select_year = data["year"]
    
    
    
    # graph codes
    economic_burden = model.transform_country_disease_new(world_data, selected_country)
    economic_burden_transformed = model.extend_years_quadratic_increment(economic_burden, 2034)

    prevalence_data = model.transform_country_disease_prevalence_new(world_data, selected_country)
    prevalence_data_transformed = model.extend_years_quadratic_increment(prevalence_data, 2034)

    # slice prevalence_data_transformed so that it only contain column of selected_disease
    prevalence_data_transformed_sliced = prevalence_data_transformed[[selected_disease]]
    economic_burden_transformed_sliced = economic_burden_transformed[[selected_disease]]
    
    economic_burden_transformed_aggregated = economic_burden_transformed.sum(axis=1)


    # convert prevalence_data_transformed_sliced so that it can be send as payload to flask requests
    prevalence_data_transformed_sliced = prevalence_data_transformed_sliced.to_dict()
    economic_burden_transformed_sliced = economic_burden_transformed_sliced.to_dict()
    
    economic_burden_transformed_sliced['economic_chart'] = economic_burden_transformed_sliced.pop(selected_disease)
    prevalence_data_transformed_sliced['prevalence_chart'] = prevalence_data_transformed_sliced.pop(selected_disease)
    
    economic_burden_transformed_sliced.update(prevalence_data_transformed_sliced)
    
    
    # economic_burden_transformed = economic_burden_transformed.to_dict()
    
    

    selected_dataframe = world_data[(world_data['Country'] == selected_country) & (world_data['Disease'] == selected_disease)]


    population = selected_dataframe['Population'].values[0]
    old_population_all = selected_dataframe['Population 40+'].values[0] 
    economic_burden_selected = economic_burden_transformed[selected_disease].loc[select_year]
    prevalence_selected = selected_dataframe['Prevalence % 40+'].values[0]


    susceptible_population_multiple = (old_population_all + (old_population_all * 0.01 * (select_year - default_year))) * prevalence_selected 


    select_year_old_population = old_population_all + (old_population_all * 0.01 * (select_year - 2024))
    susceptible_population = select_year_old_population * prevalence_selected
    # NOTE: Economic Burden below only for the undiagnosed
    economic_burden = economic_burden_selected * (susceptible_population / susceptible_population_multiple)

    # undiagnosed ratio is values of row in selected_dataframe given selected_disease and selected_country, extract values[0]
    undiagnosed_ratio = selected_dataframe['% Undiagnosed Susceptible Population 40+'].values[0]

    susceptible_population_diagnosed = susceptible_population * (1 - undiagnosed_ratio)
    susceptible_population_undiagnosed = susceptible_population * undiagnosed_ratio

    economic_burden_per_capita = economic_burden / susceptible_population

    return jsonify({
        "population": round(select_year_old_population),
        "susceptible_population": round(susceptible_population),
        "susceptible_population_diagnosed": round(susceptible_population_diagnosed),
        "susceptible_population_undiagnosed": round(susceptible_population_undiagnosed),
        "economic_burden": round(economic_burden),
        "economic_burden_per_capita": round(economic_burden_per_capita),
        # "prevalence_dataset": prevalence_data_transformed_sliced,
        "combined_dataset": economic_burden_transformed_sliced,
        "economic_burden_all_disease": economic_burden_transformed_aggregated.to_dict(),
    })

@app.route("/impact_worldwide", methods=["POST"])
def impact_worldwide():
    data = request.json

    country = data['country']
    disease = data['disease']
    clinics = data["clinic_count"]
    providers = data["provider_count"]
    capacity_pct = data["capacity_pct"]
    capacity_yearly = CONFIG["capacity_yearly"]
    # undiagnosed_ratio = CONFIG["undiagnosed_ratio"][disease]
    undiagnosed = data['susceptible_undiagnosed']
    economic_burden = data['economic_burden']

    # get undiagnosed_ratio from world_data dataset in row where in column of '% Undiagnosed Susceptible Population 40+'
    undiagnosed_ratio = world_data.loc[(world_data['Country'] == country) & (world_data['Disease'] == disease), '% Undiagnosed Susceptible Population 40+'].values[0]

    
    # Intervention calculation
    intervention_capacity = capacity_yearly * clinics * providers * capacity_pct / 100 / 20
    pct_undiag_before = undiagnosed_ratio * 100
    pct_undiag_after = max(0, pct_undiag_before * (1 - (intervention_capacity / undiagnosed))) if undiagnosed > 0 else 0

    economic_burden_after = max(0, economic_burden * (1 - intervention_capacity / undiagnosed)) if undiagnosed > 0 else 0
    economic_burden_delta = economic_burden - economic_burden_after


    return jsonify({
        "intervention_capacity": round(intervention_capacity),
        "pct_undiag_before": round(pct_undiag_before, 2),
        "pct_undiag_after": round(pct_undiag_after, 2),
        "economic_burden_after": round(economic_burden_after),
        "economic_burden_delta": round(economic_burden_delta),
        "economic_burden": round(economic_burden),
    })

if __name__ == "__main__":
    app.run(debug=True)
