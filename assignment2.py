import pandas as pd
import random
from datetime import datetime, timedelta
from sim_parameters import TRANSITION_PROBS, HOLDING_TIMES
import helper
def load(path):
    try:
        data = pd.read_csv(path)
        return data
    except Exception as e:
        print("Error while reading CSV:", e)
        return None
def create_sample_population(countries_df, selected_countries, sample_ratio):
    rows = []
    person_id = 0
    age_groups = ["less_5", "5_to_14", "15_to_24", "25_to_64", "over_65"]
    for country in selected_countries:
        row = countries_df[countries_df["country"] == country].iloc[0]
        total_pop = int(row["population"])
        sample_size = int(round(total_pop / sample_ratio))
        if sample_size <= 0:
            sample_size = 1
        for group in age_groups:
            percent = float(row[group])
            count = int(round(sample_size * percent / 100.0))
            for _ in range(count):
                rows.append([person_id, country, group])
                person_id += 1
    df = pd.DataFrame(rows, columns=["id", "country", "age_group"])
    return df
def simulate(sample_population, start_date, end_date, transition_probs, holding_times):
    import numpy as np
    all_days = pd.date_range(start=start_date, end=end_date)
    output_rows = []
    for _, person in sample_population.iterrows():
        cur_state = "H"
        prev_state = "H"
        counter = 0
        for d in all_days:
            output_rows.append([person["id"], person["age_group"], person["country"], d.strftime("%Y-%m-%d"), cur_state, counter, prev_state])
            counter += 1
            hold_time = holding_times[person["age_group"]][cur_state]
            if counter >= (hold_time if hold_time > 0 else 1):
                prev_state = cur_state
                states = list(transition_probs[person["age_group"]][cur_state].keys())
                probabilities = list(transition_probs[person["age_group"]][cur_state].values())
                cur_state = np.random.choice(states, p=probabilities)
                counter = 0
    simulated_df = pd.DataFrame(output_rows, columns=["person_id", "age_group_name", "country", "date", "state", "staying_days", "prev_state"])
    grouped = simulated_df.groupby(["date", "country", "state"]).size().reset_index(name="count")
    summary_df = grouped.pivot_table(index=["date", "country"], columns="state", values="count", fill_value=0).reset_index()
    for s in ["D", "H", "I", "M", "S"]:
        if s not in summary_df.columns:
            summary_df[s] = 0
    summary_df = summary_df[["date", "country", "D", "H", "I", "M", "S"]]
    return simulated_df, summary_df
def run(countries_csv_name, countries, start_date, end_date, sample_ratio):
    df_countries = load(countries_csv_name)
    if df_countries is None:
        print("Error: could not read input file.")
        return
    sample_population = create_sample_population(df_countries, countries, sample_ratio)
    simulated_df, summary_df = simulate(sample_population, start_date, end_date, TRANSITION_PROBS, HOLDING_TIMES)
    simulated_df.to_csv("a2-covid-simulated-timeseries.csv", index=False)
    summary_df.to_csv("a2-covid-summary-timeseries.csv", index=False)
    helper.create_plot("a2-covid-summary-timeseries.csv", countries)
    print("✅ Simulation completed successfully! Files have been created.")
