import streamlit as st
import pandas as pd
import numpy as np
import pickle
from model import Model
import requests
import json



world_data = pd.read_csv('world_data_cleaned_new.csv')

country_list = world_data['Country'].unique()


model = Model()

capacity_yearly = 110400

#create empty dataframe to store economic burden for each country and disease
economic_burden_df = pd.DataFrame(columns=['Year', 'Economic Burden ($)'])

for country in country_list:
    for disease in world_data[world_data['Country'] == country]['Disease'].unique():
        economic_burden_2 = model.transform_country_disease_new(world_data, country)
        economic_burden_transformed_2 = model.extend_years_quadratic_increment(economic_burden_2, 2034)
        temp_df = economic_burden_transformed_2[[disease]].reset_index().rename(columns={'index': 'Year', disease: 'Economic Burden ($)'})
        temp_df['Year'] = pd.to_numeric(temp_df['Year'], errors='coerce')
        economic_burden_df = pd.concat([economic_burden_df, temp_df], ignore_index=True)

# Ensure Year is numeric and sum Economic Burden by Year
economic_burden_df['Year'] = pd.to_numeric(economic_burden_df['Year'], errors='coerce')
economic_burden_df = economic_burden_df.groupby('Year', as_index=False)['Economic Burden ($)'].sum()
    



# st.dataframe(economic_burden_df, use_container_width=True)


economic_burden_df.to_csv('economic_burden_worldwide_total.csv', index=False)



st.markdown('### How Big is the Problem Projected to 2030?')

selected_country = st.selectbox('Select Country', country_list)



selected_disease = st.selectbox('Select the Non-Communicable Diseases (NCD) of Interest:', world_data[world_data['Country'] == selected_country]['Disease'].unique())





economic_burden = model.transform_country_disease_new(world_data, selected_country)
economic_burden_transformed = model.extend_years_quadratic_increment(economic_burden, 2034)

prevalence_data = model.transform_country_disease_prevalence_new(world_data, selected_country)
prevalence_data_transformed = model.extend_years_quadratic_increment(prevalence_data, 2034)

prevalence_forecast = model.line_chart(prevalence_data_transformed, selected_disease)
economic_burden_forecast = model.line_chart_economy(economic_burden_transformed, selected_disease)

# slice prevalence_data_transformed so that it only contain column of selected_disease
prevalence_data_transformed_sliced = prevalence_data_transformed[[selected_disease]]
economic_burden_transformed_sliced = economic_burden_transformed[[selected_disease]]


# convert prevalence_data_transformed_sliced so that it can be send as payload to flask requests
prevalence_data_transformed_sliced = prevalence_data_transformed_sliced.to_dict()
economic_burden_transformed_sliced = economic_burden_transformed_sliced.to_dict()



# st.dataframe(economic_burden, use_container_width=True)


st.plotly_chart(economic_burden_forecast)


st.plotly_chart(prevalence_forecast)





# st.dataframe(economic_burden)

# st.dataframe(economic_burden_transformed)



# provinces_names = provinces_data['Province'].unique()

# # add 'Indonesia (All Provinces)' to the provinces_names as the first element
# provinces_names = np.insert(provinces_names, 0, 'Indonesia (All Provinces)')
# # delete last element of provinces_names
# provinces_names = np.delete(provinces_names, -1)




# selected_provinces = st.selectbox('Select Province', provinces_names)

# if selected_provinces != 'Indonesia (All Provinces)':
#     old_population = provinces_data[provinces_data['Province'] == selected_provinces]['Population'].values[0] * old_ratio
#     ratio_to_total_population = old_population / (provinces_data['Population'].sum() * old_ratio)
#     number_of_clinics_default = provinces_data[provinces_data['Province'] == selected_provinces]['Number of Clinics'].values[0] 




default_year = 2024
select_year = st.slider('Select Year', min_value=default_year-10, max_value=default_year+10, step=1, value=default_year)

payload = {
    "country": selected_country,
    "disease": selected_disease,
    "year": select_year,
    # "economic_burden_transformed": economic_burden_transformed.to_dict(),

}

response = requests.post("http://localhost:5000/predict_worldwide", json=payload)


# selected_dataframe = world_data[(world_data['Country'] == selected_country) & (world_data['Disease'] == selected_disease)]


# population = selected_dataframe['Population'].values[0]
# old_population_all = selected_dataframe['Population 40+'].values[0] 
# economic_burden_selected = economic_burden_transformed[selected_disease].loc[select_year]
# prevalence_selected = selected_dataframe['Prevalence % 40+'].values[0]


# susceptible_population_multiple = (old_population_all + (old_population_all * 0.01 * (select_year - default_year))) * prevalence_selected 


# select_year_old_population = old_population_all + (old_population_all * 0.01 * (select_year - 2024))
# susceptible_population = select_year_old_population * prevalence_selected
# # NOTE: Economic Burden below only for the undiagnosed
# economic_burden = economic_burden_selected * (susceptible_population / susceptible_population_multiple)

# # undiagnosed ratio is values of row in selected_dataframe given selected_disease and selected_country, extract values[0]
# undiagnosed_ratio = selected_dataframe['% Undiagnosed Susceptible Population 40+'].values[0]

# susceptible_population_diagnosed = susceptible_population * (1 - undiagnosed_ratio)
# susceptible_population_undiagnosed = susceptible_population * undiagnosed_ratio

# economic_burden_per_capita = economic_burden / susceptible_population

results = response.json()

select_year_old_population = results['population']
susceptible_population_diagnosed = results['susceptible_population_diagnosed']
economic_burden = results["economic_burden"]
susceptible_population = results['susceptible_population']
susceptible_population_undiagnosed = results['susceptible_population_undiagnosed']
economic_burden_per_capita = results['economic_burden_per_capita']

st.write(results['prevalence_dataset'])



col1, col2 = st.columns(2)

with col1:
    st.metric('Population', f'{select_year_old_population:,.0f}', help='Population of age 40+ in the selected year.')
    st.metric('Susceptible Population (Diagnosed)', f'{susceptible_population_diagnosed:,.0f}', help='Based on Diagnosed to Undiagnosed Ratio')
    st.metric('Total Economic Burden (Yearly)', f'${economic_burden:,.0f}', help = 'Relative to Population of age 40%')
    
with col2:
    st.metric('Susceptible Population', f'{susceptible_population:,.0f}', help='Relative to Prevalence (%)')
    st.metric('Susceptible Population (Undiagnosed)', f'{susceptible_population_undiagnosed:,.0f}', help='Based on Diagnosed to Undiagnosed Ratio')
    st.metric('Economic Burden per Capita (Yearly)', f'${economic_burden_per_capita:,.0f}')
    st.caption('Economic Burden per Capita = Total Economic Burden / Susceptible Population')
    
# st.markdown('### Introducing our Intervention Solution')

# number_of_clinics_default = 100

# col1, col2 = st.columns(2)

# with col1:
#     st.image('clinic.png', use_container_width=True)
    
# with col2:
    
#     col3, col4 = st.columns(2)
#     with col3:
#         number_clinic = st.number_input('Number of Clinics*',  min_value=1, value=number_of_clinics_default)
        
#     with col4:
#         number_provider = st.number_input('Medical Providers per Clinic', 1)
        
#     st.caption('*New start-ups, acquired or repurposed from existing clinics') 
        
        
        
#     capacity_allocation = st.number_input('Capacity Allocation (%) to NCD', 20, help='Percentage of total capacity allocated for selected NCD (depends on demand trend)')

        
    
        
#     intervention = capacity_yearly * number_clinic * capacity_allocation / 100 * number_provider
#     intervention = intervention / 20
    
#     st.metric('Intervention Capacity (Yearly)', f'{intervention:,.0f}')
#     st.caption('Number of people to be serviced by the intervention in a year')
    
    
# percentage_undiagnosed = undiagnosed_ratio * 100
# percentage_undiagnosed = np.round(percentage_undiagnosed, 0)
# percentage_undiagnosed_after = percentage_undiagnosed * (1 - (intervention / susceptible_population_undiagnosed))
# percentage_undiagnosed_after = percentage_undiagnosed_after.round(2)
# if percentage_undiagnosed_after < 0:
#     percentage_undiagnosed_after = 0
# delta = percentage_undiagnosed_after - percentage_undiagnosed
# delta = np.round(delta, 2)

# economic_burden_after = economic_burden - (economic_burden * (intervention / susceptible_population_undiagnosed))
# if economic_burden_after < 0:
#     economic_burden_after = 0        
        
# col5, col6 = st.columns(2)
# with col5:
#     st.metric('Percentage Undiagnosed (%)', percentage_undiagnosed, help='Calculated from the ratio of Undiagnosed to Total Self-Reported and Undiagnosed combined based on Source [1]')
    
    
# with col6:
#     st.metric('Percentage Undiagnosed after Intervention (%)', percentage_undiagnosed_after, delta=delta, delta_color='inverse', help='The decrease in percentage undiagnosed is based on number of patients that can be serviced by the intervention out of the total susceptible population (undiagnosed)')


# delta_economic_burden = (economic_burden_after - economic_burden) / economic_burden * 100
# delta_economic_burden = delta_economic_burden.round(2)
    
# col7, col8 = st.columns(2)

# with col7:
#     st.metric('Total Economic Burden (Before)', f'${economic_burden:,.0f}')
# with col8:
#     st.metric('Total Economic Burden (After)', f'${economic_burden_after:,.0f}')
    
# col10, col11 = st.columns(2)

# with col10:
#         st.metric('Economic Burden Reduction', f'${(economic_burden - economic_burden_after):,.0f}', delta=delta_economic_burden, delta_color='inverse')

# st.markdown("### Visualize Impact")

# st.markdown("##### % Undiagnosed Before and After Intervention")

# col1, col2 = st.columns(2)

# colors_before = ['gold', 'mediumturquoise', 'darkorange']
# colors_after = ['gold', 'darkorange']


# with col1:
    
#     fig = model.create_pie_chart(['Diagnosed', 'Undiagnosed'], [(100-percentage_undiagnosed), percentage_undiagnosed], colors=colors_after)

#     st.plotly_chart(fig)

    
# with col2:



#     fig = model.create_pie_chart(['Diagnosed', 'Diagnosed due Intervention', 'Undiagnosed'], [(100-percentage_undiagnosed), -delta,(percentage_undiagnosed+delta)], colors=colors_before)
#     st.plotly_chart(fig)
    

# st.markdown("##### Economic Burden Before and After Intervention")

# col3, col4 = st.columns(2)

# value_max = (economic_burden)  * (susceptible_population / susceptible_population_multiple) # * (0.49 / economic_burden)
# value_max = int(value_max)


# scale = max(int(round(economic_burden / 20 / 1_000_000) * 1_000_000), 1_000_000) # 1 million


# with col3:
#     pictogram = model.create_pictogram(economic_burden, scale, value_max , emoji_symbol='💵', columns=7, vertical_shift=0.5, zoom_ratio=1.2)
#     st.plotly_chart(pictogram, use_container_width=True, key='before_intervention')

# with col4:
#     pictogram = model.create_pictogram(economic_burden_after, scale, value_max, emoji_symbol='💵', columns=7, vertical_shift=0.5, zoom_ratio=1.2) 
#     st.plotly_chart(pictogram, use_container_width=True, key='after_intervention')
    
# st.markdown("### Opportunities to Collaborate in Closing the Healthcare Gap")
# st.markdown(
#     "There are numerous ways you can join us in addressing this healthcare disparity and "
#     "alleviating the global economic burden."
# )

# st.markdown("- **Start or Invest in Health Stores**  \n"
#             "  Become part of the solution.")

# st.markdown("- **Partner with Us as Healthcare Professionals**  \n"
#             "  Collaborate with us to make a difference.")

# st.markdown("- **Donate Genia.AI Devices for Early Detection**  \n"
#             "  Support our mission to enhance early diagnosis.")

# st.markdown("- **Invest in Us to Accelerate Our Solutions**  \n"
#             "  Help us expedite the development of our innovative approaches.")
    
    
    
# st.divider()


# st.markdown('##### References')

# # write using st.write 
# # Tenggara, B. P. S. P. S. (n.d.). Jumlah Penduduk Menurut Provinsi di Indonesia (ribu),  2019-2023 - Tabel Statistik. Badan Pusat Statistik Provinsi Sulawesi Tenggara. https://sultra.bps.go.id/id/statistics-table/1/NDc3OCMx/jumlah-penduduk-menurut-provinsi-di-indonesia--ribu----2019-2023.html

# # write using st.write
# # BPS (Badan Pusat Statistik) Indonesia. (2020). Statistik Penduduk Indonesia 2020. Badan Pusat Statistik. https://www.bps.go.id/publication/2021/04/27/3c4e8d6f9b5a2f3d7c9a4d1a/statistik-penduduk-indonesia-2020.html


# # st.link_button("[1] Indonesia's 2020 NCD Prevalence and Economic Burden Data", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4051736/", type='secondary')
# # # write using st.write
# # st.link_button("[2] BPS (Badan Pusat Statistik) Indonesia Population Across Provinces - 2020", "https://sultra.bps.go.id/id/statistics-table/1/NDc3OCMx/jumlah-penduduk-menurut-provinsi-di-indonesia--ribu----2019-2023.html", type='secondary')
# # st.link_button("[3] BPS (Badan Pusat Statistik) Indonesia Population by Age Group - 2020", "https://www.bps.go.id/en/statistics-table/2/NzE1IzI=/total-population-of-age-15-and-above-by-age-group.html", type='secondary')