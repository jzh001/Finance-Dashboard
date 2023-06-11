import streamlit as st
import finance_data_scraper as scraper
import pandas as pd
from pages import *


def getDashboard(selectedIndex):
    st.title(f"{selectedIndex} Dashboard")

    selectedTicker, indexTicker, duration = getSideBar(selectedIndex)
    try:
        tickerInfo = scraper.getInfo(selectedTicker)
    except:
        st.write("Data Unavailable: Check your Inputs")
        return
    
    stockData = scraper.getYahooHistorical(
        selectedTicker, duration=duration)

    mainCols = st.columns([3, 0.1, 1.5])

    with mainCols[0]:

        if selectedTicker == indexTicker:
            candleTab, lineTab, strategiesTab, dataTab, economyTab = st.tabs(
                ["Candlesticks", "Trendline", "Strategies", "Data", "Economy"])
        else:
            candleTab, lineTab, strategiesTab, dividendTab, managemtTab, dataTab, economyTab = st.tabs(
                ["Candlesticks", "Trendline", "Strategies", "Dividends", "Management", "Data", "Economy"])

        if scraper.getCountryFromIndex(selectedIndex) == "SG":
            interestData = scraper.getMASInterestData(duration=duration)
            exchangeData = scraper.getMASExchangeRateData(duration=duration)
        else:
            interestData = pd.DataFrame()
            exchangeData = pd.DataFrame()
        
        with candleTab:
            getCandlestickChart(stockData, selectedTicker)
            getVolumeChart(stockData)
            getMacroChartsTab(interestData, exchangeData, duration, "candle")
        with lineTab:
            getLineChart(stockData, selectedTicker)
            getVolumeChart(stockData)
            getMacroChartsTab(interestData, exchangeData, duration, "line")
        with strategiesTab:
            intervalHours = scraper.getIntervalfromDuration(duration)
            if scraper.convertDurationToHours("3mo") <= scraper.convertDurationToHours(duration):
                getMovingAveragesChart(stockData, intervalHours)
            getResistSupportChart(stockData)
            getMomentumChart(stockData)
        if selectedTicker != indexTicker:
            with dividendTab:
                getDividendCharts(selectedTicker)
        if selectedTicker != indexTicker:
            with managemtTab:
                getPayChart(tickerInfo, selectedTicker, indexTicker)

        with dataTab:
            getDataTab(stockData, interestData)

        with economyTab:
            getEconomyTab(stockData, interestData, exchangeData, duration)


            

    with mainCols[2]:
        st.markdown(f"### [{selectedTicker}] {tickerInfo['shortName']}")
        if selectedTicker != indexTicker:
            st.write(f"{tickerInfo['sector']}: {tickerInfo['industryDisp']}")
            with st.expander("Business Summary"):
                st.write(tickerInfo['longBusinessSummary'])

            with st.expander("Stock Fundamentals"):
                fundDf = pd.DataFrame(scraper.getFinancialData(selectedTicker))
                st.dataframe(fundDf.style.set_properties(
                    **{'text-align': 'center'}), use_container_width=True, height=600)
        try:
            # getNews occasionally runs into JSON Decode error
            getNews(selectedTicker)
        except:
            pass


