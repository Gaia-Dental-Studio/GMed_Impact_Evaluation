import streamlit as st
import pandas as pd
import numpy as np
import pickle
from model import Model


def app():

    prevalence_data = pd.read_csv('indonesia_ncd_prevalence_cleaned.csv', index_col=0)
    economic_burden_data = pd.read_csv('indonesia_ncd_economic_burden_cleaned.csv', index_col=0)
    economic_burden_undiagnosed_data = pd.read_csv('indonesia_ncd_economic_burden_undiagnosed_cleaned.csv', index_col=0)
    provinces_data = pd.read_csv('provinces_population.csv')

    # convert provinces_data['Population'] by removing the "", get rid the commas and convert to int
    provinces_data['Population'] = provinces_data['Population'].fillna('0')  # Replace NaN with '0'
    provinces_data['Population'] = provinces_data['Population'].str.replace('"', '').str.replace(',', '').astype(int)


    model = Model()
    
    old_population = 32424300.0
    old_ratio = 32424300.0 / 282477584.0

    old_population_all = 32424300.0

    capacity_yearly = 110400
    undiagnosed_ratio = {'Diabetes': 0.75, 'Hypertension': 0.6667, 'Heart Problem': 0.93, 'Stroke': 0.887, 
                        #  'Dementia': 0.3, 'Pregnancy': 0.3, 'Stunting': 0.3, 'Menopouse': 0.3
                         }
    
    ratio_to_total_population = 1
    
    
    number_of_clinics_default = provinces_data['Number of Clinics'].values[-1] 
    number_of_clinics_default = int(number_of_clinics_default)
    
    


    st.markdown('### How Big is the Problem Projected to 2034?')

    selected_disease = st.selectbox('Select the Non-Communicable Diseases (NCD) of Interest:', prevalence_data.columns)


    prevalence_forecast = model.line_chart(prevalence_data, selected_disease)
    economic_burden_forecast = model.line_chart_economy(economic_burden_data, selected_disease)


    st.plotly_chart(prevalence_forecast)

    st.plotly_chart(economic_burden_forecast)
    
    st.markdown('#### At a Glance: Economic Burden of NCDs Compared')
    # tab1,tab2 = st.tabs(['Economic Burden of NCDs', 'Economic Burden of NCDs (Undiagnosed)'])
    fig_compare, df_long = model.line_chart_economy_disease_compare(economic_burden_data, columns=None, top=5)
    st.plotly_chart(fig_compare, use_container_width=True)
    
    # st.dataframe(df_long, use_container_width=True, hide_index=True)
    df_long.to_csv('economic_burden_compare.csv', index=False)
    
    
    st.divider()
    
    st.markdown('### Introducing our Intervention Solution: GMedCC Health Stores')
    st.write('GMedCC Health Stores offer low footprint and set up costs, with maximum connectivity')



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

    select_year = st.slider('Select Year', 2014, 2034, 2024, 1)

    susceptible_population_multiple = (old_population_all + (old_population_all * 0.016 * (select_year - 2024))) * prevalence_data[selected_disease].loc[select_year] / 100


    select_year_old_population = old_population + (old_population * 0.016 * (select_year - 2024))
    susceptible_population = select_year_old_population * prevalence_data[selected_disease].loc[select_year] / 100
    # NOTE: Economic Burden below only for the undiagnosed
    economic_burden = economic_burden_undiagnosed_data[selected_disease].loc[select_year] * (susceptible_population / susceptible_population_multiple)



    susceptible_population_diagnosed = susceptible_population * (1 - undiagnosed_ratio[selected_disease])
    susceptible_population_undiagnosed = susceptible_population * undiagnosed_ratio[selected_disease]

    economic_burden_per_capita = economic_burden / susceptible_population_undiagnosed

    col1, col2 = st.columns(2)

    with col1:
        st.metric('Population', f'{select_year_old_population:,.0f}', help='The population of Age 40+, which ratio is assumed to be same across all provinces. Source [2] for population data across provinces, and source [3] for distribution of age 40+ population')
        st.metric('Susceptible Population (Diagnosed)', f'{susceptible_population_diagnosed:,.0f}')
        st.metric('Total Economic Burden (Yearly)', f'${economic_burden:,.0f}', help="Only represents for Undiagnosed cases of Age 40+ and susceptible proportionally to the population of Age 40+")
        
    with col2:
        st.metric('Susceptible Population', f'{susceptible_population:,.0f}', )
        st.metric('Susceptible Population (Undiagnosed)', f'{susceptible_population_undiagnosed:,.0f}', )
        st.metric('Economic Burden per Capita (Yearly)', f'${economic_burden_per_capita:,.0f}', help='Amount assumed to be equal across all provinces.')
        st.caption('Economic Burden per Capita = Total Economic Burden / Susceptible Population')
        
    st.markdown('### Introducing our Intervention Solution')

    col1, col2 = st.columns(2)

    with col1:
        st.image('clinic_2.png', use_container_width=True)
        
    with col2:
        
        col3, col4 = st.columns(2)
        with col3:
            number_clinic = st.number_input('Number of Clinics*',  min_value=1, value=number_of_clinics_default)
            
        with col4:
            number_provider = st.number_input('Medical Providers per Clinic', 1)
            
        st.caption('*New start-ups, acquired or repurposed from existing clinics') 
            
            
            
        capacity_allocation = st.number_input('Capacity Allocation (%) to NCD', 20, help='Percentage of total capacity allocated for selected NCD (depends on demand trend)')

            
            
        intervention = capacity_yearly * number_clinic * capacity_allocation / 100 * number_provider
        intervention = intervention / 20
        
        st.metric('Intervention Capacity (Yearly)', f'{intervention:,.0f}')
        st.caption('Number of people to be serviced by the intervention in a year')
        
        
    percentage_undiagnosed = undiagnosed_ratio[selected_disease] * 100
    percentage_undiagnosed = np.round(percentage_undiagnosed, 0)
    percentage_undiagnosed_after = percentage_undiagnosed * (1 - (intervention / susceptible_population_undiagnosed))
    percentage_undiagnosed_after = percentage_undiagnosed_after.round(2)
    if percentage_undiagnosed_after < 0:
        percentage_undiagnosed_after = 0
    delta = percentage_undiagnosed_after - percentage_undiagnosed
    delta = np.round(delta, 2)

    economic_burden_after = economic_burden - (economic_burden * (intervention / susceptible_population_undiagnosed))
    if economic_burden_after < 0:
        economic_burden_after = 0        
            
    col5, col6 = st.columns(2)
    with col5:
        st.metric('Percentage Undiagnosed (%)', percentage_undiagnosed, )
        
        
    with col6:
        st.metric('Percentage Undiagnosed after Intervention (%)', percentage_undiagnosed_after, delta=delta, delta_color='inverse', help='The decrease in percentage undiagnosed is based on number of patients that can be serviced by the intervention out of the total susceptible population (undiagnosed)')


    delta_economic_burden = (economic_burden_after - economic_burden) / economic_burden * 100
    delta_economic_burden = delta_economic_burden.round(2)
        
    col7, col8 = st.columns(2)

    with col7:
        st.metric('Total Economic Burden (Before)', f'${economic_burden:,.0f}')
    with col8:
        st.metric('Total Economic Burden (After)', f'${economic_burden_after:,.0f}')
        
    col10, col11 = st.columns(2)

    with col10:
            st.metric('Economic Burden Reduction', f'${(economic_burden - economic_burden_after):,.0f}', delta=delta_economic_burden, delta_color='inverse')

    st.markdown("### Visualize Impact")

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

    # st.write(economic_burden)
    # st.write(susceptible_population)
    # st.write(susceptible_population_multiple)

    col3, col4 = st.columns(2)

    value_max = (economic_burden) * (susceptible_population / susceptible_population_multiple)
    value_max = int(value_max) if value_max > 0 else 10000000


    if selected_provinces == 'Indonesia (All Provinces)':
        scale = 40000000
    else:
        scale = 10000000 


    with col3:
        pictogram = model.create_pictogram(economic_burden, scale, value_max , emoji_symbol='💵', columns=7, vertical_shift=0.5, zoom_ratio=1.2)
        st.plotly_chart(pictogram, use_container_width=True, key='before_intervention')
    
    with col4:
        pictogram = model.create_pictogram(economic_burden_after, scale, value_max, emoji_symbol='💵', columns=7, vertical_shift=0.5, zoom_ratio=1.2) 
        st.plotly_chart(pictogram, use_container_width=True, key='after_intervention')
        
        

    st.markdown("### Opportunities to Collaborate in Closing the Healthcare Gap")
    st.markdown(
        "There are numerous ways you can join us in addressing this healthcare disparity and "
        "alleviating the global economic burden."
    )

    st.markdown("- **Start or Invest in Health Stores**  \n"
                "  Become part of the solution.")

    st.markdown("- **Partner with Us as Healthcare Professionals**  \n"
                "  Collaborate with us to make a difference.")

    st.markdown("- **Donate Genia.AI Devices for Early Detection**  \n"
                "  Support our mission to enhance early diagnosis.")

    st.markdown("- **Invest in Us to Accelerate Our Solutions**  \n"
                "  Help us expedite the development of our innovative approaches.")

        
    st.divider()


    st.markdown('##### References')
    
    st.info('This model calculator is developed based upon various reliable data sources ranged from year of 2010 to 2024. References detailed as follows')


    # write using st.write 
    # Tenggara, B. P. S. P. S. (n.d.). Jumlah Penduduk Menurut Provinsi di Indonesia (ribu),  2019-2023 - Tabel Statistik. Badan Pusat Statistik Provinsi Sulawesi Tenggara. https://sultra.bps.go.id/id/statistics-table/1/NDc3OCMx/jumlah-penduduk-menurut-provinsi-di-indonesia--ribu----2019-2023.html

    # write using st.write
    # BPS (Badan Pusat Statistik) Indonesia. (2020). Statistik Penduduk Indonesia 2020. Badan Pusat Statistik. https://www.bps.go.id/publication/2021/04/27/3c4e8d6f9b5a2f3d7c9a4d1a/statistik-penduduk-indonesia-2020.html


    # st.link_button("[1] Indonesia's 2020 NCD Prevalence and Economic Burden Data", "https://pmc.ncbi.nlm.nih.gov/articles/PMC4051736/", type='secondary')
    # write using st.write
    st.link_button("[2] BPS (Badan Pusat Statistik) Indonesia Population Across Provinces - 2020", "https://sultra.bps.go.id/id/statistics-table/1/NDc3OCMx/jumlah-penduduk-menurut-provinsi-di-indonesia--ribu----2019-2023.html", type='secondary')
    st.link_button("[3] BPS (Badan Pusat Statistik) Indonesia Population by Age Group - 2020", "https://www.bps.go.id/en/statistics-table/2/NzE1IzI=/total-population-of-age-15-and-above-by-age-group.html", type='secondary')