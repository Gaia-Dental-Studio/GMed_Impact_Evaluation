import streamlit as st 

import streamlit_1 as indonesia_model
import streamlit_2 as worldwide_model




st.title('Size of the Problem and What We can Do Collectively')


indonesia_model.app()


# options = ["Indonesia", "Worldwide"]
# selection = st.pills("Select Base", options, selection_mode="single")


# if selection == "Indonesia":
#     indonesia_model.app()
    
# elif selection == "Worldwide":
#     worldwide_model.app()