import streamlit as st
import pandas as pd
import numpy as np
import pickle
from model import Model


st.title('GMedcc: Measuring Problem and Intervention Solution')

prevalence_data = pd.read_csv('ncd_prevalence_cleaned.csv', index_col=0)
economic_burden_data = pd.read_csv('ncd_economic_burden_cleaned.csv', index_col=0)
provinces_data = pd.read_csv('provinces_population.csv')

# convert provinces_data['Population'] by removing the "", get rid the commas and convert to int
provinces_data['Population'] = provinces_data['Population'].fillna('0')  # Replace NaN with '0'
provinces_data['Population'] = provinces_data['Population'].str.replace('"', '').str.replace(',', '').astype(int)


model = Model()
old_population = 98665006
old_ratio = 98665006 / 205360436

old_population_all = 98665006

capacity_yearly = 110400
undiagnosed_ratio = {'Diabetes': 0.29, 'Hypertension': 0.63, 'Cancer': 0.7, 'Heart Disease': 0.82}
ratio_to_total_population = 1
number_of_clinics_default = provinces_data['Number of Clinics'].values[-1] 
number_of_clinics_default = int(number_of_clinics_default)


st.markdown('### How big the problem is and will be?')

selected_disease = st.selectbox('Select NCD', prevalence_data.columns, help="Source: [1] Indonesia's 2020 NCD Prevalence and Economic Burden Data")


prevalence_forecast = model.line_chart(prevalence_data, selected_disease)
economic_burden_forecast = model.line_chart_economy(economic_burden_data, selected_disease)


st.plotly_chart(prevalence_forecast)

st.plotly_chart(economic_burden_forecast)


provinces_names = provinces_data['Province'].unique()

# add 'Indonesia (All Provinces)' to the provinces_names as the first element
provinces_names = np.insert(provinces_names, 0, 'Indonesia (All Provinces)')
# delete last element of provinces_names
provinces_names = np.delete(provinces_names, -1)




selected_provinces = st.selectbox('Select Province', provinces_names)

if selected_provinces != 'Indonesia (All Provinces)':
    old_population = provinces_data[provinces_data['Province'] == selected_provinces]['Population'].values[0] * old_ratio
    ratio_to_total_population = old_population / (provinces_data['Population'].sum() * old_ratio)
    number_of_clinics_default = provinces_data[provinces_data['Province'] == selected_provinces]['Number of Clinics'].values[0] 

select_year = st.slider('Select Year', 2010, 2030, 2020, 1)

susceptible_population_multiple = (old_population_all + (old_population_all * 0.01 * (select_year - 2020))) * prevalence_data[selected_disease].loc[select_year] / 100


select_year_old_population = old_population + (old_population * 0.01 * (select_year - 2020))
susceptible_population = select_year_old_population * prevalence_data[selected_disease].loc[select_year] / 100
economic_burden = economic_burden_data[selected_disease].loc[select_year] * (susceptible_population / susceptible_population_multiple)
economic_burden_per_capita = economic_burden / susceptible_population



col1, col2 = st.columns(2)

with col1:
    st.metric('Population', f'{select_year_old_population:,.0f}', help='The population of Age 40+, which ratio is assumed to be same across all provinces. Source [2] for population data across provinces, and source [3] for distribution of age 40+ population')
    st.metric('Total Economic Burden (Yearly)', f'${economic_burden*1000000000:,.0f}', help="Assumed to be contributed only by the population of age 40+ who are undiagnosed and susceptible. Source: [1]")
    
with col2:
    st.metric('Susceptible Population', f'{susceptible_population:,.0f}')
    st.metric('Economic Burden per Capita (Yearly)', f'${economic_burden_per_capita*1000000000:,.0f}', help='Amount assumed to be equal across all provinces.')
    st.caption('Economic Burden per Capita = Total Economic Burden / Susceptible Population')
    
st.markdown('### Introducing our Intervention Solution')

col1, col2 = st.columns(2)

with col1:
    st.image('clinic.png', use_container_width=True)
    
with col2:
    
    col3, col4 = st.columns(2)
    with col3:
        number_clinic = st.number_input('Number of Clinics',  min_value=1, value=number_of_clinics_default)
        capacity_allocation = st.number_input('Capacity Allocation (%)', 20, help='Percentage of total capacity allocated for selected NCD (depends on demand trend)')
    with col4:
        number_provider = st.number_input('Number of Medical Provider', 1)
        
    intervention = capacity_yearly * number_clinic * capacity_allocation / 100 * number_provider
    
    st.metric('Intervention Capacity (Yearly)', f'{intervention/20:,.0f}')
    st.caption('Number of people can be serviced by the intervention')
    
    
percentage_undiagnosed = undiagnosed_ratio[selected_disease] * 100
percentage_undiagnosed_after = percentage_undiagnosed * (1 - (intervention / susceptible_population))
percentage_undiagnosed_after = percentage_undiagnosed_after.round(2)
delta = percentage_undiagnosed_after - percentage_undiagnosed
delta = delta.round(2)

economic_burden_after = economic_burden - (economic_burden * (intervention / susceptible_population))
        
col5, col6 = st.columns(2)
with col5:
    st.metric('Percentage Undiagnosed (%)', percentage_undiagnosed)
    
    
with col6:
    st.metric('Percentage Undiagnosed after Internvention (%)', percentage_undiagnosed_after, delta=delta, delta_color='inverse')


delta_economic_burden = (economic_burden_after - economic_burden) / economic_burden * 100
delta_economic_burden = delta_economic_burden.round(2)
    
col7, col8 = st.columns(2)

with col7:
    st.metric('Total Economic Burden (Before)', f'${economic_burden*1000000000:,.0f}')
with col8:
    st.metric('Total Economic Burden (After)', f'${economic_burden_after*1000000000:,.0f}')
    
col10, col11 = st.columns(2)

with col10:
        st.metric('Economic Burden Reduction', f'${(economic_burden - economic_burden_after)*1000000000:,.0f}', delta=delta_economic_burden, delta_color='inverse')

st.markdown("### Visualizing Impact")

st.markdown("##### % Undiagnosed Before and After Intervention")

col1, col2 = st.columns(2)

colors_before = ['gold', 'mediumturquoise', 'darkorange']
colors_after = ['gold', 'darkorange']


with col1:
    
    fig = model.create_pie_chart(['Diagnosed', 'Undiagnosed'], [(100-percentage_undiagnosed), percentage_undiagnosed], colors=colors_after)

    st.plotly_chart(fig)

    
with col2:



    fig = model.create_pie_chart(['Diagnosed', 'Diagnosed due Intervention', 'Undiagnosed'], [(100-percentage_undiagnosed), -delta,(percentage_undiagnosed+delta)], colors=colors_before)
    st.plotly_chart(fig)
    

st.markdown("##### Economic Burden Before and After Intervention")

col3, col4 = st.columns(2)

value_max = (1000000000 * economic_burden ) * (1.93 / economic_burden)
value_max = int(value_max)


if selected_provinces == 'Indonesia (All Provinces)':
    scale = 40000000
else:
    scale = 20000000 

with col3:
    pictogram = model.create_pictogram(economic_burden*1000000000, scale, value_max , emoji_symbol='💵', columns=7, vertical_shift=0.5, zoom_ratio=1.2)
    st.plotly_chart(pictogram, use_container_width=True, key='before_intervention')
   
with col4:
    pictogram = model.create_pictogram(economic_burden_after*1000000000, scale, value_max, emoji_symbol='💵', columns=7, vertical_shift=0.5, zoom_ratio=1.2) 
    st.plotly_chart(pictogram, use_container_width=True, key='after_intervention')
    
st.divider()


st.markdown('##### References')

# write using st.write 
# Tenggara, B. P. S. P. S. (n.d.). Jumlah Penduduk Menurut Provinsi di Indonesia (ribu),  2019-2023 - Tabel Statistik. Badan Pusat Statistik Provinsi Sulawesi Tenggara. https://sultra.bps.go.id/id/statistics-table/1/NDc3OCMx/jumlah-penduduk-menurut-provinsi-di-indonesia--ribu----2019-2023.html

# write using st.write
# BPS (Badan Pusat Statistik) Indonesia. (2020). Statistik Penduduk Indonesia 2020. Badan Pusat Statistik. https://www.bps.go.id/publication/2021/04/27/3c4e8d6f9b5a2f3d7c9a4d1a/statistik-penduduk-indonesia-2020.html


st.link_button("[1] Indonesia's 2020 NCD Prevalence and Economic Burden Data", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4051736/", type='secondary')
# write using st.write
st.link_button("[2] BPS (Badan Pusat Statistik) Indonesia Population Across Provinces - 2020", "https://sultra.bps.go.id/id/statistics-table/1/NDc3OCMx/jumlah-penduduk-menurut-provinsi-di-indonesia--ribu----2019-2023.html", type='secondary')
st.link_button("[3] BPS (Badan Pusat Statistik) Indonesia Population by Age Group - 2020", "https://www.bps.go.id/en/statistics-table/2/NzE1IzI=/total-population-of-age-15-and-above-by-age-group.html", type='secondary')