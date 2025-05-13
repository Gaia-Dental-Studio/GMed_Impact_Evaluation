import streamlit as st
import pandas as pd

def calculate_linear_growth_rate(df: pd.DataFrame) -> float:
    """
    Calculate the average annual increase in prevalence using simple linear regression.

    Parameters:
    - df (pd.DataFrame): DataFrame with columns 'Year' and 'Prevalence' (in decimal)

    Returns:
    - float: average annual increase in prevalence (in percentage points)
    """
    # Ensure correct column names
    if 'Year' not in df.columns or 'Prevalence' not in df.columns:
        raise ValueError("DataFrame must contain 'Year' and 'Prevalence' columns")

    x = df['Year']
    y = df['Prevalence'] * 100  # Convert decimal to percentage for interpretation

    x_mean = x.mean()
    y_mean = y.mean()

    covariance = ((x - x_mean) * (y - y_mean)).mean()
    variance = ((x - x_mean) ** 2).mean()

    slope = covariance / variance  # Percentage points per year
    return slope / 100

# Example Data
example_df = pd.DataFrame({
    'Year': [2019, 2021, 2024],
    'Prevalence': [0.10, 0.09, 0.15]
})

st.title("Average Annual Prevalence Increase (Linear Growth)")

# Editable table
edited_df = st.data_editor(example_df, num_rows="dynamic")

# Only compute if valid data
try:
    avg_increase = calculate_linear_growth_rate(edited_df)
    st.write(f"### Average Annual Increase: `{avg_increase:.3f}` per year")
except Exception as e:
    st.error(f"Error: {e}")
