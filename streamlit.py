import streamlit as st
import pandas as pd
import numpy as np
import pickle
from model import Model


st.title('GMedcc: Measuring Problem and Intervention Solution')

prevalence_data = pd.read_csv('ncd_prevalence_cleaned.csv', index_col=0)
economic_burden_data = pd.read_csv('ncd_economic_burden_cleaned.csv', index_col=0)


model = Model()
old_population = 98665006
capacity_yearly = 110400
undiagnosed_ratio = {'Diabetes': 0.29, 'Hypertension': 0.63, 'Cancer': 0.7, 'Heart Disease': 0.82}


st.markdown('### How big the problem is and will be?')

selected_disease = st.selectbox('Select NCD', prevalence_data.columns)


prevalence_forecast = model.line_chart(prevalence_data, selected_disease)
economic_burden_forecast = model.line_chart_economy(economic_burden_data, selected_disease)


st.plotly_chart(prevalence_forecast)

st.plotly_chart(economic_burden_forecast)



select_year = st.slider('Select Year', 2010, 2030, 2020, 1)

select_year_old_population = old_population + (old_population * 0.01 * (select_year - 2020))
susceptible_population = select_year_old_population * prevalence_data[selected_disease].loc[select_year] / 100
economic_burden = economic_burden_data[selected_disease].loc[select_year]
economic_burden_per_capita = economic_burden / susceptible_population

col1, col2 = st.columns(2)

with col1:
    st.metric('Population', f'{select_year_old_population:,.0f}')
    st.metric('Total Economic Burden (Yearly)', f'${economic_burden*1000000000:,.0f}')
    
with col2:
    st.metric('Susceptible Population', f'{susceptible_population:,.0f}')
    st.metric('Economic Burden per Capita (Yearly)', f'${economic_burden_per_capita*1000000000:,.0f}')
    st.caption('Economic Burden per Capita = Total Economic Burden / Susceptible Population')
    
st.markdown('### Introducing our Intervention Solution')

col1, col2 = st.columns(2)

with col1:
    st.image('clinic.png', use_container_width=True)
    
with col2:
    
    col3, col4 = st.columns(2)
    with col3:
        number_clinic = st.number_input('Number of Clinics', 1)
        capacity_allocation = st.number_input('Capacity Allocation (%)', 20, help='Percentage of total capacity allocated for selected NCD (depends on demand trend)')
    with col4:
        number_provider = st.number_input('Number of Medical Provider', 1)
        
    intervention = capacity_yearly * number_clinic * capacity_allocation / 100 * number_provider
    
    st.metric('Intervention Capacity (Yearly)', f'{intervention:,.0f}')
    
    
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
