import streamlit as st
import stock_dashboard
import housing_dashboard

st.set_page_config(layout="wide")

navOption =st.sidebar.selectbox("Asset Type",options=["Stock Market", "Property Market"])

if navOption == "Stock Market":
    stockType = st.sidebar.selectbox(
        'Select Index / ETF',
        ('STI', 'SG REIT', 'S&P 500', 'Custom')
    )
    stock_dashboard.getDashboard(stockType)
elif navOption == "Property Market":
    housing_dashboard.getDashboard()
    


