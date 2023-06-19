import streamlit as st
import stock_dashboard
import housing_data_scraper

st.set_page_config(layout="wide")

navOption =st.sidebar.selectbox("Navigation",options=["Stock Market", "Real Estate"])

if navOption == "Stock Market":
    stockType = st.sidebar.selectbox(
        'Select Index / ETF',
        ('STI', 'SG REIT', 'S&P 500', 'Custom')
    )
    stock_dashboard.getDashboard(stockType)
elif navOption == "Real Estate":
    st.write(housing_data_scraper.getResaleHDBPrices()[::-1].reset_index(drop=True))
    


