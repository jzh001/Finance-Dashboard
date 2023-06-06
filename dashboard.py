import streamlit as st
import finance_data_scraper as scraper
import altair as alt
import webbrowser
import pandas as pd


def getDashboard(index):
    st.title(f"{index} Dashboard")
    indexTicker, symbols = scraper.getSymbols(index)

    # List of options for the dropdown
    symbolOptions = [indexTicker] + symbols["Symbol"].tolist()

    # Dropdown component
    selectedTicker = st.sidebar.selectbox(
        "Ticker", symbolOptions, index=symbolOptions.index(indexTicker))

    duration = st.sidebar.selectbox(
        "Duration", ["3mo", "6mo", "YTD", "1y", "5y", "10y"], index=4)
    interval = st.sidebar.selectbox(
        "Interval", ["1d", "5d", "1wk", "1mo"], index=2)

    tickerInfo = scraper.getInfo(selectedTicker)

    # Check if the selected option is the custom option
    if selectedTicker == "Custom":
        custom_input = st.sidebar.text_input("Enter a custom option")
        if custom_input:
            selectedTicker = custom_input

    data = scraper.getYahooHistorical(
        selectedTicker, duration=duration, interval=interval)

    lineChart = alt.Chart(data).mark_line(size=2).encode(
        x=alt.X("date", title="Date"),
        y=alt.Y('close', scale=alt.Scale(zero=False), title="Close")
    ).properties(height=600, title=selectedTicker).interactive()

    candlestickChart = alt.Chart(data).mark_rule(size=1).encode(
        x=alt.X("date", title="Date"),
        y=alt.Y('low:Q', scale=alt.Scale(zero=False), title="Low"),
        y2=alt.Y2('high:Q', title="High"),
        color=alt.condition(
            'datum.close > datum.open',
            alt.value('#2ecc71'),  # green color for bullish days
            alt.value('#e74c3c')   # red color for bearish days
        )
    )

    candlestickChart += candlestickChart.mark_bar(size=4).encode(
        alt.Y('open:Q', scale=alt.Scale(zero=False), title="Open"),
        alt.Y2('close:Q', title="Close"),
    )

    candlestickChart = candlestickChart.properties(
        height=600, title=selectedTicker).interactive()

    volumeChart = alt.Chart(data).mark_bar(size=0.5).encode(
        x=alt.X("date", title="Date"),
        y=alt.Y('volume', scale=alt.Scale(zero=False), title="Volume"),
        color=alt.condition(
            'datum.close > datum.open',
            alt.value('#2ecc71'),  # green color for bullish days
            alt.value('#e74c3c')   # red color for bearish days
        )
    ).properties(height=200).interactive()
    try:
        payChart = alt.Chart(pd.DataFrame(tickerInfo["companyOfficers"])).mark_bar().encode(
            x=alt.X("totalPay", title="Total Pay"),
            y=alt.Y("title", title="Title"),

        ).properties(height=600, title=selectedTicker).interactive()
    except:
        pass

    mainCols = st.columns([3, 0.1, 1.5])

    with mainCols[0]:
        candleTab, lineTab, managemtTab, dataTab, industryTab = st.tabs(
            ["Candlesticks", "Trendline", "Management", "Data", "Industry"])
        cols = st.columns(5)

        with candleTab:
            st.altair_chart(candlestickChart, use_container_width=True)
            st.altair_chart(volumeChart, use_container_width=True)
        with lineTab:
            st.altair_chart(lineChart, use_container_width=True)
            st.altair_chart(volumeChart, use_container_width=True)
        with managemtTab:
            if selectedTicker != indexTicker:
                try:
                    st.altair_chart(payChart, use_container_width=True)
                except:
                    pass
                st.dataframe(data=pd.DataFrame(tickerInfo["companyOfficers"]).style.set_properties(
                    **{'text-align': 'center'}), use_container_width=True)
            else:
                st.write("N/A")
        with dataTab:
            if selectedTicker != indexTicker:
                selectedRow = symbols[symbols['Symbol'] ==
                                      selectedTicker].reset_index(drop=True).T
                selectedRow.columns = ["Attributes"]
                st.sidebar.write(selectedRow.style.set_properties(
                    **{'text-align': 'center'}))
            st.dataframe(data=data.style.set_properties(
                **{'text-align': 'center'}), use_container_width=True, height=600)
            # st.dataframe(data=SP500.style.set_properties(**{'text-align': 'center'}),use_container_width=True)

    with mainCols[2]:
        st.markdown(f"## [{selectedTicker}] {tickerInfo['shortName']}")
        if selectedTicker != indexTicker:
            st.write(f"{tickerInfo['sector']}: {tickerInfo['industryDisp']}")
            with st.expander("Business Summary"):
                st.write(tickerInfo['longBusinessSummary'])

            with st.expander("Stock Fundamentals"):
                # items = ["dividendRate", "dividendYield", "marketCap", "profitMargins", "floatShares", "sharesOutstanding", "sharesPercentSharesOut", "heldPercentInsiders", "heldPercentInstitutions", "impliedSharesOutstanding",
                #          "bookValue", "priceToBook", "earningsQuarterlyGrowth", "trailingEps", "forwardEps", "totalCashPerShare", "debtToEquity", "revenuePerShare", "returnOnAssets", "returnOnEquity", "operatingMargins", "ebitdaMargins", ]

                # fundDf = pd.DataFrame({(key, val) for key, val in tickerInfo.items() if key in items})
                fundDf = pd.DataFrame(scraper.getFinancialData(selectedTicker))
                # fundDf.columns = ["Metric", "Value"]
                # fundDf.set_index("Metric", inplace=True)

                st.dataframe(fundDf.style.set_properties(
                    **{'text-align': 'center'}), use_container_width=True, height=600)

            st.markdown("## News")
            allNews = [news for news in scraper.getNews(
                selectedTicker) if "thumbnail" in news]
            for news in allNews[:5]:
                cols = st.columns([1, 0.3, 4.5, 1])
                with cols[0]:
                    st.write("")
                    try:
                        st.image(news['thumbnail']['resolutions'][1]['url'])
                    except:
                        st.image(news['thumbnail']['resolutions'][0]['url'])
                with cols[2]:
                    st.markdown(f"#### {news['title']}")
                    st.write(news['publisher'])
                with cols[3]:
                    st.write("")
                    st.write("")
                    if st.button("More >", key=news['link']):
                        webbrowser.open_new_tab(news['link'])
