import streamlit as st
import pandas as pd
import numpy as np
import json
from model import Model

# Load JSON configuration
with open('parameters.json') as f:
    CONFIG = json.load(f)

# Load data
prevalence_data = pd.read_csv('indonesia_ncd_prevalence_cleaned.csv', index_col=0)
econ_data = pd.read_csv('indonesia_ncd_economic_burden_cleaned.csv', index_col=0)
econ_burden_undiag_data = pd.read_csv("indonesia_ncd_economic_burden_undiagnosed_cleaned.csv", index_col=0)
provinces_data = pd.read_csv('provinces_population.csv')
provinces_data['Population'] = provinces_data['Population'].fillna('0') \
    .str.replace('"', '', regex=False).str.replace(',', '', regex=False).astype(int)

# Model instance
model = Model()

# Intervention logic (previously in Flask)
def run_intervention_model(disease, province, year, clinics, providers, capacity_pct):
    old_ratio = CONFIG["old_ratio"]
    old_population_all = CONFIG["old_population_all"]
    growth_rate = CONFIG["growth_rate"]
    capacity_yearly = CONFIG["capacity_yearly"]
    undiagnosed_ratio = CONFIG["undiagnosed_ratio"][disease]

    if province == "Indonesia (All Provinces)":
        old_population = old_population_all
    else:
        old_population = provinces_data[provinces_data["Province"] == province]["Population"].values[0] * old_ratio

    projected_pop = old_population * (1 + growth_rate * (year - 2024))
    prevalence_pct = prevalence_data[disease].loc[year]
    susceptible_population = projected_pop * prevalence_pct / 100

    projected_pop_all = old_population_all * (1 + growth_rate * (year - 2024))
    susceptible_all = projected_pop_all * prevalence_pct / 100

    burden_unit_cost = econ_burden_undiag_data[disease].loc[year]
    economic_burden = burden_unit_cost * (susceptible_population / susceptible_all)

    diagnosed = susceptible_population * (1 - undiagnosed_ratio)
    undiagnosed = susceptible_population * undiagnosed_ratio
    econ_burden_per_capita = economic_burden / undiagnosed if undiagnosed > 0 else 0

    intervention_capacity = capacity_yearly * clinics * providers * capacity_pct / 100 / 20
    pct_undiag_before = undiagnosed_ratio * 100
    pct_undiag_after = max(0, pct_undiag_before * (1 - (intervention_capacity / undiagnosed))) if undiagnosed > 0 else 0

    economic_burden_after = max(0, economic_burden * (1 - intervention_capacity / undiagnosed)) if undiagnosed > 0 else 0
    economic_burden_delta = economic_burden - economic_burden_after

    return {
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
    }



st.title('Size of the Problem and What We can Do Collectively')
st.markdown('### How Big is the Problem Projected to 2034?')

default_clinics = int(provinces_data['Number of Clinics'].values[-1])
diseases = list(CONFIG['undiagnosed_ratio'].keys())

selected_disease = st.selectbox('Select the Non-Communicable Diseases (NCD) of Interest:', diseases)
st.plotly_chart(model.line_chart(prevalence_data, selected_disease))
st.plotly_chart(model.line_chart_economy(econ_data, selected_disease))

# st.markdown('#### At a Glance: Economic Burden of NCDs Compared')
# fig_compare, df_long = model.line_chart_economy_disease_compare(econ_data, top=5)
# st.plotly_chart(fig_compare, use_container_width=True)
# df_long.to_csv('economic_burden_compare.csv', index=False)

st.divider()

st.markdown('### Introducing our Intervention Solution: GMedCC Health Stores')
st.write('GMedCC Health Stores offer low footprint and set up costs, with maximum connectivity')

provinces_names = np.insert(provinces_data['Province'].unique(), 0, 'Indonesia (All Provinces)')
provinces_names = np.delete(provinces_names, -1)
selected_province = st.selectbox('Select Province', provinces_names)

year = st.slider('Select Year', 2014, 2034, 2024)

col1, col2 = st.columns(2)
with col1:
    st.image('clinic_2.png', width=300)
with col2:
    clinic_count = st.number_input('Number of Clinics*', min_value=1, value=default_clinics)
    provider_count = st.number_input('Medical Providers per Clinic', min_value=1)
    st.caption('*New start-ups, acquired or repurposed from existing clinics')
    capacity_pct = st.number_input('Capacity Allocation (%) to NCD', min_value=1, max_value=100, value=20)

# Replaced API call with direct function
result = run_intervention_model(selected_disease, selected_province, year, clinic_count, provider_count, capacity_pct)

# === UI display logic remains unchanged ===
# you can now use all values from `result` as before

# (insert your existing metrics, charts, and explanations using `result[...]` here)


population = result["population"]
susceptible = result["susceptible_population"]
diagnosed = result["susceptible_diagnosed"]
undiagnosed = result["susceptible_undiagnosed"]
econ_burden_total = result["economic_burden"]
econ_burden_per_capita = result["economic_burden_per_capita"]
intervention_capacity = result["intervention_capacity"]
pct_undiag_before = result["pct_undiag_before"]
pct_undiag_after = result["pct_undiag_after"]
econ_burden_after = result["economic_burden_after"]
econ_burden_delta = result["economic_burden_delta"]

col1, col2 = st.columns(2)
with col1:
    st.metric('Population', f'{population:,.0f}')
    st.metric('Susceptible Population (Diagnosed)', f'{diagnosed:,.0f}')
    st.metric('Total Economic Burden (Yearly)', f'${econ_burden_total:,.0f}')
with col2:
    st.metric('Susceptible Population', f'{susceptible:,.0f}')
    st.metric('Susceptible Population (Undiagnosed)', f'{undiagnosed:,.0f}')
    st.metric('Economic Burden per Capita (Yearly)', f'${econ_burden_per_capita:,.0f}')
    st.caption('Economic Burden per Capita = Total Economic Burden / Susceptible Population')

st.markdown('### Introducing our Intervention Solution')

st.metric('Intervention Capacity (Yearly)', f'{intervention_capacity:,.0f}')

delta_pct = round(pct_undiag_after - pct_undiag_before, 2)
col3, col4 = st.columns(2)
with col3:
    st.metric('Percentage Undiagnosed (%)', pct_undiag_before)
with col4:
    st.metric('Undiagnosed After Intervention (%)', pct_undiag_after, delta=delta_pct, delta_color='inverse')

delta_pct_econ = round((econ_burden_after - econ_burden_total) / econ_burden_total * 100, 2)
col5, col6 = st.columns(2)
with col5:
    st.metric('Economic Burden (Before)', f'${econ_burden_total:,.0f}')
with col6:
    st.metric('Economic Burden (After)', f'${econ_burden_after:,.0f}')

st.metric('Economic Burden Reduction', f'${econ_burden_delta:,.0f}', delta=delta_pct_econ, delta_color='inverse')

st.markdown("### Visualize Impact")
st.markdown("##### % Undiagnosed Before and After Intervention")

col1, col2 = st.columns(2)
with col1:
    st.plotly_chart(model.create_pie_chart(['Diagnosed', 'Undiagnosed'],
                                            [100 - pct_undiag_before, pct_undiag_before],
                                            colors=['gold', 'darkorange']))
with col2:
    st.plotly_chart(model.create_pie_chart(['Diagnosed', 'Diagnosed due Intervention', 'Undiagnosed'],
                                            [100 - pct_undiag_before, -delta_pct, pct_undiag_before + delta_pct],
                                            colors=['gold', 'mediumturquoise', 'darkorange']))

st.markdown("##### Economic Burden Before and After Intervention")
scale = 40000000 if selected_province == 'Indonesia (All Provinces)' else 10000000
pictogram_max = int(econ_burden_total * susceptible / (CONFIG['old_population_all'] * (1 + CONFIG['growth_rate'] * (year - 2024)) * prevalence_data[selected_disease].loc[year] / 100))

col3, col4 = st.columns(2)
with col3:
    st.plotly_chart(model.create_pictogram(econ_burden_total, scale, pictogram_max, emoji_symbol='💵',
                                            columns=7, vertical_shift=0.5, zoom_ratio=1.2),
                    use_container_width=True)
with col4:
    st.plotly_chart(model.create_pictogram(econ_burden_after, scale, pictogram_max, emoji_symbol='💵',
                                            columns=7, vertical_shift=0.5, zoom_ratio=1.2),
                    use_container_width=True)

st.markdown("### Opportunities to Collaborate in Closing the Healthcare Gap")
st.markdown("- **Start or Invest in Health Stores**  \nBecome part of the solution.")
st.markdown("- **Partner with Us as Healthcare Professionals**  \nCollaborate with us to make a difference.")
st.markdown("- **Donate Genia.AI Devices for Early Detection**  \nSupport our mission to enhance early diagnosis.")
st.markdown("- **Invest in Us to Accelerate Our Solutions**  \nHelp us expedite innovation.")

st.divider()

st.markdown('##### References')
st.info("This model calculator is developed based upon various reliable data sources ranging from 2010 to 2024.")
st.link_button("[2] BPS Indonesia Population Across Provinces - 2020",
                "https://sultra.bps.go.id/id/statistics-table/1/NDc3OCMx/jumlah-penduduk-menurut-provinsi-di-indonesia--ribu----2019-2023.html",
                type='secondary')
st.link_button("[3] BPS Indonesia Population by Age Group - 2020",
                "https://www.bps.go.id/en/statistics-table/2/NzE1IzI=/total-population-of-age-15-and-above-by-age-group.html",
                type='secondary')
