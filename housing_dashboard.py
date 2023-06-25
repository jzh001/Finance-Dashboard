import housing_data_scraper
import streamlit as st
import altair as alt
import folium
import pandas as pd
from streamlit_folium import st_folium


def getDashboard():
    st.title("Property Market")
    indexTab, resaleHdbTab = st.tabs(["Price Index", "HDB Resale"])
    with resaleHdbTab:
        getResaleHdbTab()
        st.write(housing_data_scraper.getResaleHDBPrices()[::-1][:1000].reset_index(drop=True))


def getResaleHdbTab():
    df = housing_data_scraper.getResaleHDBPrices()
    getResaleHdbBarChart(df)
    plotHdbMapDistribution(df)


def getResaleHdbBarChart(df):
    category_counts = df['town'].value_counts().reset_index()
    category_counts.columns = ['Town', 'Sales']
    chart = alt.Chart(category_counts).mark_bar().encode(
        x='Town',
        y='Sales'
    )

    # Set the chart properties
    chart = chart.properties(
        # Adjust the width of the bars as per your preference
        width=alt.Step(40)
    )

    # Display the chart using Streamlit
    st.altair_chart(chart, use_container_width=True)

def plotHdbMapDistribution(df):
    town = df['town'].value_counts().reset_index()
    town.columns = ['town', 'frequency']
    map = folium.Map()

    # Loop through the street_counts DataFrame to add circle markers to the map
    for _, row in town.iterrows():
        town = row['town']
        frequency = row['frequency']
        location = get_location(town)
        print(location)

        if location:
            # Add the circle marker to the map
            folium.CircleMarker(
                location=location,
                radius=frequency * 0.0005,
                color='blue',
                fill=True,
                fill_color='blue'
            ).add_to(map)

    # call to render Folium map in Streamlit
    st_data = st_folium(map, width=725)

def get_location(town):
    df = pd.read_csv('data/Town Coords.csv')
    df.set_index('town', inplace=True)
    try:
        lat, lon = df['lat'][town], df['lon'][town]
        return lat, lon
    except:
        return None