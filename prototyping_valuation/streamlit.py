import streamlit as st
import pandas as pd
import plotly.express as px
from currency_converter import CurrencyConverter
import matplotlib.pyplot as plt



st.title('Prototyping Valuation')

st.markdown('### Parameter Definition')

col1, col2, col3 = st.columns(3)

with col1:
    scenario = st.pills("Scenario", ["Low Bound", "High Bound"], default="Low Bound")
    
with col2:
    device_procurement_status = st.pills("Device Procurement to be Executed", ["Yes", "No"], default="Yes")
    
with col3:
    currency = st.pills("Currency", ["IDR", "AUD"], default="IDR")
    
    
st.divider()

if device_procurement_status == "Yes":

    st.markdown('### Procurement/Manufacturing Variables')

    col1, col2, col3 = st.columns(3)

    default_value_one_lead = 500 if scenario == "High Bound" else 300
    default_value_six_leads = 100 if scenario == "High Bound" else 50
    default_value_all_in_one = 200 if scenario == "High Bound" else 100

    with col1:
        procurement_count_one_lead = st.number_input("Device to Procure (One Lead) - ECG", min_value=0, step=100, value=default_value_one_lead, format="%d")

    with col2:
        procurement_count_six_leads = st.number_input("Device to Procure (6 Leads) - ECG", min_value=0, step=50, value=default_value_six_leads, format="%d")
        
    with col3:
        procurement_count_all_in_one = st.number_input("Device to Procure - All in One", min_value=0, step=100, value=default_value_all_in_one, format="%d")


    c = CurrencyConverter()

    def get_procurement_cost_one_lead(procurement_count_one_lead, currency):
        
        unit_cost = 45 if procurement_count_one_lead < 1000 else 40
        cost = procurement_count_one_lead * unit_cost
        
        if currency == "IDR":
            cost = c.convert(cost, 'AUD', 'IDR')
            
        return cost

    def get_procurement_cost_six_leads(procurement_count_six_leads, currency):
        unit_cost = 450 if procurement_count_six_leads < 1000 else 400
        cost = procurement_count_six_leads * unit_cost
        
        if currency == "IDR":
            cost = c.convert(cost, 'AUD', 'IDR')
            
        return cost
    
    def get_procurement_cost_all_in_one(procurement_count_all_in_one, currency):

        unit_cost = 1900000 
        cost = procurement_count_all_in_one * unit_cost

        if currency == "AUD":
            cost = c.convert(cost, 'IDR', 'AUD')
            
        return cost

        
    col1, col2 = st.columns(2)

    procurement_one_lead_cost = get_procurement_cost_one_lead(procurement_count_one_lead, currency)
    procurement_six_leads_cost = get_procurement_cost_six_leads(procurement_count_six_leads, currency)
    procurement_all_in_one_cost = get_procurement_cost_all_in_one(procurement_count_all_in_one, currency)

    with col1:
        st.metric("Procurement Cost (One Lead) - ECG", f"{procurement_one_lead_cost:,.0f} {currency}", delta=None)
        st.metric("Procurement Cost (All in One) - ECG", f"{procurement_all_in_one_cost:,.0f} {currency}", delta=None)

    with col2:
        st.metric("Procurement Cost (6 Leads) - ECG", f"{procurement_six_leads_cost:,.0f} {currency}", delta=None)



    shipment_from = st.pills("Shipment From", ["China", "India", "Germany", "Singapore"], default="China")

    total_unit = procurement_count_one_lead + procurement_count_six_leads + procurement_count_all_in_one

    def get_logistics_tax(scenario, shipment_from, total_unit, currency):
        
        logistic_cost_low = {
            'China': 2500000,
            'India': 4500000,
            'Germany': 6000000,
            'Singapore': 1500000
        } #in IDR
        logistic_cost_high = {
            'China': 3500000,
            'India': 5000000,
            'Germany': 6000000,
            'Singapore': 2000000
        } #in IDR
        
        #logistic is per 10 kg, item is 2 kg
        
        logistic_cost_high = {k: v * (total_unit / 5) for k, v in logistic_cost_high.items()}
        logistic_cost_low = {k: v * (total_unit / 5) for k, v in logistic_cost_low.items()}
        

        import_duty_tax = 0.15
        value_added_tax = 0.11
        income_tax_prepayment = 0.075
        
        if scenario == "Low Bound":
            cost = logistic_cost_low[shipment_from]
        else:
            cost = logistic_cost_high[shipment_from]
    
        tax = cost * (import_duty_tax + value_added_tax + income_tax_prepayment)
        
        if currency == "IDR":
            return cost, tax
        else:
            return c.convert(cost, 'IDR', 'AUD'), c.convert(tax, 'IDR', 'AUD')
        
        
    logistics_cost, tax = get_logistics_tax(scenario, shipment_from, total_unit, currency)

    # create plotly horizontal bar chart for procurement_one_lead_cost, procurement_six_leads_cost, logistics_cost, tax
    cost_labels = ['Procurement One Lead', 'Procurement Six Leads', 'Procurement All in One', 'Logistics Cost', 'Tax']
    cost_values = [procurement_one_lead_cost, procurement_six_leads_cost, procurement_all_in_one_cost, logistics_cost, tax]
    cost_colors = ['#1f77b4', '#ff7f0e', "#ff8dd7",'#2ca02c', '#d62728']

    # Sort cost_labels and cost_values in descending order of cost_values
    sorted_items = sorted(zip(cost_values, cost_labels, cost_colors), reverse=False)
    sorted_cost_values, sorted_cost_labels, sorted_cost_colors = zip(*sorted_items)

    fig = px.bar(
        x=sorted_cost_values,
        y=sorted_cost_labels,
        orientation='h',
        color=sorted_cost_labels,
        color_discrete_sequence=sorted_cost_colors,
        labels={'x': f'Cost ({currency})', 'y': ''},
        title='Procurement and Logistics Costs Breakdown'
    )
    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)




st.divider()

st.markdown('### Use of Funds per Category')

data = pd.read_csv('prototyping_cost_cleaned.csv')

def selected_amount(scenario, currency):
    if scenario == "Low Bound" and currency == "IDR":
        return "Amount Low"
    elif scenario == "High Bound" and currency == "IDR":
        return "Amount High"
    elif scenario == "Low Bound" and currency == "AUD":
        return "Amount AUD Low"
    elif scenario == "High Bound" and currency == "AUD":
        return "Amount AUD High"


if device_procurement_status == "No":
    data = data[data['Needed Pre-Product'] == "Yes"]
    


grouped_data = data.groupby('Category').agg({selected_amount(scenario, currency): 'sum'}).reset_index()


marketing_cost = grouped_data[grouped_data['Category'] == 'Marketing'][selected_amount(scenario, currency)].values[0]
rnd_cost = grouped_data[grouped_data['Category'] == 'R&D'][selected_amount(scenario, currency)].values[0]
# manufacturing_row = grouped_data[grouped_data['Category'] == 'Manufacturing']
if device_procurement_status == "No":
    manufacturing_cost = 0
else:
    manufacturing_cost = procurement_one_lead_cost + procurement_six_leads_cost + procurement_all_in_one_cost + logistics_cost + tax
operational_cost = grouped_data[grouped_data['Category'] == 'Operational'][selected_amount(scenario, currency)].values[0]




# st.dataframe(grouped_data, use_container_width=True)



col3, col4 = st.columns(2)
with col3:
    # use st.metric but apply currency formatting for IDR and AUD
    st.metric("Marketing Cost", f"{marketing_cost:,.0f} {currency}", delta=None)
    st.metric("R&D Cost", f"{rnd_cost:,.0f} {currency}", delta=None)

    st.metric("Manufacturing Cost", f"{manufacturing_cost:,.0f} {currency}", delta=None)
    
    st.metric("Operational Cost", f"{operational_cost:,.0f} {currency}", delta=None)
with col4:
    
    # use plotly pie chart to visualize the cost distribution
    
    # add manufacturing cost to grouped_data using pd.concat
    new_row = pd.DataFrame([{'Category': 'Manufacturing', selected_amount(scenario, currency): manufacturing_cost}])
    grouped_data = pd.concat([grouped_data, new_row], ignore_index=True)
    
    fig = px.pie(grouped_data, values=selected_amount(scenario, currency), names='Category', 
                #  title='Cost Distribution by Category', 
                 color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)
    

group_subcategory = data.groupby(['Category', 'Sub-Category']).agg({selected_amount(scenario, currency): 'sum'}).reset_index()

# add procurement_one_lead_cost, procurement_six_leads_cost, procurement_all_in_one_cost, logistics_cost, tax to manufacturing subcategory
if device_procurement_status == "Yes":
    manufacturing_subcategory = pd.DataFrame({
        'Category': ['Manufacturing'] * 5,
        'Sub-Category': [
            'Procurement One Lead',
            'Procurement Six Leads',
            'Procurement All in One',
            'Logistics Cost',
            'Tax'
        ],
        selected_amount(scenario, currency): [
            procurement_one_lead_cost,
            procurement_six_leads_cost,
            procurement_all_in_one_cost,
            logistics_cost,
            tax
        ]
    })
    group_subcategory = pd.concat([group_subcategory, manufacturing_subcategory], ignore_index=True)

    # Format the last column (amount) to have no decimal places
    amount_col = selected_amount(scenario, currency)
    group_subcategory[amount_col] = round(group_subcategory[amount_col], 0)

st.dataframe(group_subcategory, use_container_width=True, hide_index=True)



st.divider()
variable_cost =  manufacturing_cost
fixed_cost = marketing_cost + rnd_cost + operational_cost

    

total_cost = marketing_cost + rnd_cost + manufacturing_cost + operational_cost

# using plotly create stack horizontal bar chart of variable_cost and fixed_cost
# Sample data



# Prepare data
data = pd.DataFrame({
    'Cost Type': ['Variable Cost', 'Fixed Cost'],
    'Value': [variable_cost, fixed_cost]
})

# Calculate total and percentage
total_cost = data['Value'].sum()
data['Percentage'] = data['Value'] / total_cost * 100
data['Label'] = data.apply(lambda row: f"{row['Cost Type']}<br>{row['Percentage']:.1f}%", axis=1)

# Create treemap
fig_cost = px.treemap(
    data,
    path=['Cost Type'],
    values='Value',
    color='Cost Type',
    color_discrete_map={'Variable Cost': "#6bb5ea", 'Fixed Cost': "#ffaa60"},
    custom_data=['Label']
)

# Update hover, label text, and font size
fig_cost.update_traces(
    hovertemplate='%{customdata[0]}<br>Value: %{value}<extra></extra>',
    textinfo='label+percent entry',
    texttemplate='%{customdata[0]}',
    textfont=dict(size=20)  # <-- Set font size here
)

fig_cost.update_layout(
    title='Total Cost Breakdown',
    margin=dict(t=50, l=25, r=25, b=25)
)

st.plotly_chart(fig_cost, use_container_width=True)

col1, col2 = st.columns(2)

with col1:
    st.metric("Variable Cost", f"{variable_cost:,.0f} {currency}", delta=None)
    
with col2:
    st.metric("Fixed Cost", f"{fixed_cost:,.0f} {currency}", delta=None)
    

st.metric("Total Cost", f"{total_cost:,.0f} {currency}", delta=None)