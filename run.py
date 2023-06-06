import streamlit as st
import dashboard

st.set_page_config(layout="wide")

stockType = st.sidebar.selectbox(
    'Select Stocks',
    ('S&P 500', 'STI', 'SG REIT', 'Custom')
)

dashboard.getDashboard(stockType)


    


