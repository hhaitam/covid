import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
import ast  # For safely parsing JSON-like strings

# Load data from CSV
@st.cache_data  # Cache the data to avoid reloading on every interaction
def load_data():
    df = pd.read_csv("covid_data_monthly.csv")
    
    # Extract country names and ISO codes from the 'region' column
    df['country'] = df['region'].apply(lambda x: ast.literal_eval(x)['name'])
    df['iso_alpha'] = df['region'].apply(lambda x: ast.literal_eval(x)['iso'])
    
    return df

# Function to process data for plotting (aggregate by day)
def process_data(df, selected_countries, start_date, end_date):
    # Convert 'date' to datetime and filter by date range
    df['date'] = pd.to_datetime(df['date']).dt.date
    df = df[(df['date'] >= start_date) & (df['date'] <= end_date)]

    # Filter data for selected countries
    df = df[df['country'].isin(selected_countries)]

    # Aggregate data by date and country (sum values for each day)
    aggregated_df = df.groupby(['date', 'country', 'iso_alpha'], as_index=False).agg({
        'confirmed': 'sum',
        'deaths': 'sum',
        'recovered': 'sum'
    })

    return aggregated_df

# Streamlit app
def main():
    st.title("COVID-19 Data Visualization")
    st.write("Select a date range (maximum one year) and countries to compare COVID-19 statistics.")

    # Load data from CSV
    df = load_data()

    # List of available countries
    available_countries = df['country'].unique().tolist()

    # Debug: Print available countries
    #st.write("Available Countries:", available_countries)

    # Wheel list (multiselect dropdown) for country selection
    selected_countries = st.multiselect(
        "Select Countries",
        available_countries,
        default=[available_countries[0]] if available_countries else []  # Default to the first country if available
    )

    # Date range picker with a maximum interval of one year
    min_date = datetime(2020, 3, 9).date()  # Minimum date for the date picker
    max_date = datetime(2023, 3, 9).date()  # Maximum date for the date picker
    start_date = st.date_input("Start Date", min_date, min_value=min_date, max_value=max_date)
    end_date = st.date_input("End Date", max_date, min_value=min_date, max_value=max_date)

    # Ensure the date range is no more than one year
    if (end_date - start_date).days > 365:
        st.error("Error: The date range must be no more than one year.")
        return

    if start_date > end_date:
        st.error("Error: End date must be after start date.")
        return

    if not selected_countries:
        st.info("Please select at least one country.")
        return

    # Process data for the selected date range and countries
    aggregated_df = process_data(df, selected_countries, start_date, end_date)

    # Handle missing recovery data by filling with 0
    aggregated_df['recovered'] = aggregated_df['recovered'].fillna(0)

    # Calculate the highest values for confirmed, deaths, and recovered, and their corresponding countries
    max_confirmed = aggregated_df['confirmed'].max()
    max_confirmed_country = aggregated_df.loc[aggregated_df['confirmed'].idxmax(), 'country']

    max_deaths = aggregated_df['deaths'].max()
    max_deaths_country = aggregated_df.loc[aggregated_df['deaths'].idxmax(), 'country']

    max_recovered = aggregated_df['recovered'].max()
    max_recovered_country = aggregated_df.loc[aggregated_df['recovered'].idxmax(), 'country']

    # Display the highest values and their corresponding countries in individual boxes
    st.subheader("Highest Values")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric(label="Highest Confirmed Cases", value=max_confirmed, delta=f"Country: {max_confirmed_country}")
    with col2:
        st.metric(label="Highest Deaths", value=max_deaths, delta=f"Country: {max_deaths_country}")
    with col3:
        st.metric(label="Highest Recovered Cases", value=max_recovered, delta=f"Country: {max_recovered_country}")

    # Create a map showing the selected countries and their total confirmed, deaths, and recovered cases
    st.subheader("Map of Selected Countries")
    map_data = aggregated_df.groupby(['country', 'iso_alpha'], as_index=False).agg({
        'confirmed': 'sum',
        'deaths': 'sum',
        'recovered': 'sum'
    })
    fig_map = px.choropleth(
        map_data,
        locations='iso_alpha',  # ISO Alpha-3 country codes
        color='confirmed',  # Color by confirmed cases
        hover_name='country',  # Show country name on hover
        hover_data=['confirmed', 'deaths', 'recovered'],  # Additional data to show on hover
        labels={'confirmed': 'Confirmed Cases', 'deaths': 'Deaths', 'recovered': 'Recovered Cases'},
        title='Total Confirmed Cases by Country'
    )
    st.plotly_chart(fig_map)

    # Create separate line charts for confirmed, deaths, and recovered
    st.subheader("Confirmed Cases Over Time")
    fig_confirmed = px.line(
        aggregated_df,
        x='date',
        y='confirmed',
        color='country',
        labels={'confirmed': 'Confirmed Cases', 'date': 'Date'},
        title='Confirmed Cases Over Time'
    )
    st.plotly_chart(fig_confirmed)

    st.subheader("Deaths Over Time")
    fig_deaths = px.line(
        aggregated_df,
        x='date',
        y='deaths',
        color='country',
        labels={'deaths': 'Deaths', 'date': 'Date'},
        title='Deaths Over Time'
    )
    st.plotly_chart(fig_deaths)

    st.subheader("Recovered Cases Over Time")
    fig_recovered = px.line(
        aggregated_df,
        x='date',
        y='recovered',
        color='country',
        labels={'recovered': 'Recovered Cases', 'date': 'Date'},
        title='Recovered Cases Over Time'
    )
    st.plotly_chart(fig_recovered)

if __name__ == "__main__":
    main()