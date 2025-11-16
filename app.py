import streamlit as st
import pandas as pd
import os
import assignment2

st.title("A3 Test Runner")

SAMPLE_RATIO = st.number_input("Sample Ratio", value=1000000.0, step=100000.0)
START_DATE = st.date_input("Start Date", value=pd.to_datetime("2021-04-01"))
END_DATE = st.date_input("End Date", value=pd.to_datetime("2022-04-30"))

countries_df = pd.read_csv("a2-countries.csv")
country_list = countries_df["country"].tolist()
SELECTED_COUNTRIES = st.multiselect("Select Countries", country_list, default=["Sweden"])

if st.button("Run"):
    with st.spinner("Running simulation..."):
        assignment2.run(
            countries_csv_name="a2-countries.csv",
            countries=SELECTED_COUNTRIES,
            start_date=str(START_DATE),
            end_date=str(END_DATE),
            sample_ratio=SAMPLE_RATIO,
        )
    if os.path.exists("a2-covid-simulation.png"):
        st.image("a2-covid-simulation.png", use_container_width=True)
    else:
        st.write("Simulation completed, but image not found.")
