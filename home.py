import streamlit as st 

import streamlit_1 as indonesia_model
import streamlit_2 as worldwide_model



st.title('GMedcc: Measuring Problem and Intervention Solution')

options = ["Indonesia", "Worldwide"]
selection = st.pills("Select Base", options, selection_mode="single")


if selection == "Indonesia":
    indonesia_model.app()
    
elif selection == "Worldwide":
    worldwide_model.app()