import streamlit as st
import finance_data_scraper as scraper
import altair as alt
import webbrowser
import pandas as pd
import numpy as np


def getDashboard(selectedIndex):
    st.title(f"{selectedIndex} Dashboard")

    selectedTicker, indexTicker, duration = getSideBar(selectedIndex)
    try:
        tickerInfo = scraper.getInfo(selectedTicker)
    except:
        st.write("Data Unavailable: Check your Inputs")
        return
    
    data = scraper.getYahooHistorical(
        selectedTicker, duration=duration)

    mainCols = st.columns([3, 0.1, 1.5])

    with mainCols[0]:

        if selectedTicker == indexTicker:
            candleTab, lineTab, strategiesTab, dataTab, industryTab = st.tabs(
                ["Candlesticks", "Trendline", "Strategies", "Data", "Industry"])
        else:
            candleTab, lineTab, strategiesTab, dividendTab, managemtTab, dataTab, industryTab = st.tabs(
                ["Candlesticks", "Trendline", "Strategies", "Dividends", "Management", "Data", "Industry"])

        with candleTab:
            getCandlestickChart(data, selectedTicker)
            getVolumeChart(data)
        with lineTab:
            getLineChart(data, selectedTicker)
            getVolumeChart(data)
        with strategiesTab:
            intervalHours = scraper.getIntervalfromDuration(duration)
            if scraper.convertDurationToHours("3mo") <= scraper.convertDurationToHours(duration):
                getMovingAveragesChart(data, intervalHours)
            getResistSupportChart(data)
            getMomentumChart(data)
        if selectedTicker != indexTicker:
            with dividendTab:
                getDividendCharts(selectedTicker)
        if selectedTicker != indexTicker:
            with managemtTab:
                getPayChart(tickerInfo, selectedTicker, indexTicker)

        with dataTab:
            st.dataframe(data=data[::-1].reset_index(drop=True).style.set_properties(
                **{'text-align': 'center'}), use_container_width=True, height=600)
            # st.dataframe(data=SP500.style.set_properties(**{'text-align': 'center'}),use_container_width=True)

        with industryTab:
            if selectedTicker == indexTicker:
                pass
            else:
                if selectedIndex == "S&P 500":
                    getIndustryTab(selectedTicker, selectedIndex)
                else:
                    pass

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


def getSideBar(selectedIndex):
    if selectedIndex != 'Custom':
        indexTicker, symbols = scraper.getSymbols(selectedIndex)

        # List of options for the dropdown
        symbolOptions = [indexTicker] + symbols["Symbol"].tolist()

        # Dropdown component
        selectedTicker = st.sidebar.selectbox(
            "Ticker", symbolOptions, index=symbolOptions.index(indexTicker))

    else:
        selectedTicker = st.sidebar.text_input(
            "Custom Ticker", max_chars=7, value="AAPL")
        indexTicker = "Custom"

    duration = st.sidebar.selectbox(
        "Duration", ["1d", "5d", "1wk", "1mo", "3mo", "6mo", "YTD", "1y", "5y", "10y"], index=7)
    

    if selectedIndex != 'Custom' and selectedTicker != indexTicker:
        selectedRow = symbols[symbols['Symbol'] ==
                              selectedTicker].reset_index(drop=True).T
        selectedRow.columns = ["Attributes"]
        st.sidebar.write(selectedRow.style.set_properties(
            **{'text-align': 'center'}))
        
    # Check if the selected option is the custom option
    if selectedTicker == "Custom":
        custom_input = st.sidebar.text_input("Enter a custom option")
        if custom_input:
            selectedTicker = custom_input
    
    return selectedTicker, indexTicker, duration


def getLineChart(data, selectedTicker):
    cols = st.columns(6)
    with cols[-1]:
        use_log_scale = st.checkbox('Use Logarithmic Scale')
    lineChart = alt.Chart(data).mark_line(size=2).encode(
        x=alt.X("date", title="Date"),
        y=alt.Y('close', scale=alt.Scale(zero=False,type='linear' if not use_log_scale else 'log'), title="Close")
    ).properties(height=400, title=selectedTicker).interactive()
    st.altair_chart(lineChart, use_container_width=True)


def getVolumeChart(data):
    volumeChart = alt.Chart(data).mark_bar(size=0.5).encode(
        x=alt.X("date", title="Date"),
        y=alt.Y('volume', scale=alt.Scale(zero=False), title="Volume"),
        color=alt.condition(
            'datum.close > datum.open',
            alt.value('#2ecc71'),  # green color for bullish days
            alt.value('#e74c3c')   # red color for bearish days
        )
    ).properties(height=200).interactive()
    st.altair_chart(volumeChart, use_container_width=True)


def getCandlestickChart(data, selectedTicker):
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
        height=400, title=selectedTicker).interactive()
    st.altair_chart(candlestickChart, use_container_width=True)


def getDividendCharts(selectedTicker):
    dividendData = scraper.getDividendData(selectedTicker)
    dividendByYear = scraper.getDividendDataByYear(
        selectedTicker, dividendData)

    dividendChart = alt.Chart(dividendData).mark_line(size=2).encode(
        x=alt.X("date", title="Date"),
        y=alt.Y('dividends', scale=alt.Scale(
            zero=False), title="Dividends ($)")
    ).properties(height=250, title=selectedTicker).interactive()

    dividendPercentChart = alt.Chart(dividendData).mark_line(size=2).encode(
        x=alt.X("date", title="Date"),
        y=alt.Y('dividendPercent', scale=alt.Scale(
            zero=False), title="Dividends (%)")
    ).properties(height=250, title=selectedTicker).interactive()

    dividendYearChart = alt.Chart(dividendByYear).mark_line(size=2).encode(
        x=alt.X("date", title="Date"),
        y=alt.Y('dividends', scale=alt.Scale(
            zero=False), title="Dividends ($)")
    ).properties(height=250, title=selectedTicker).interactive()

    dividendYearPercentChart = alt.Chart(dividendByYear).mark_line(size=2).encode(
        x=alt.X("date", title="Date"),
        y=alt.Y('dividendPercent', scale=alt.Scale(
            zero=False), title="Dividends (%)")
    ).properties(height=250, title=selectedTicker).interactive()

    col1, col2 = st.columns(2)
    with col1:
        st.subheader("Dividend Payments")
        st.altair_chart(dividendChart, use_container_width=True)
        st.altair_chart(dividendPercentChart, use_container_width=True)
    with col2:
        st.subheader("Dividend Payments Grouped By Year")
        st.altair_chart(dividendYearChart, use_container_width=True)
        st.altair_chart(dividendYearPercentChart, use_container_width=True)

    st.dataframe(
        data=dividendData[::-1].reset_index(drop=True), use_container_width=True, height=250)


def getPayChart(tickerInfo, selectedTicker, indexTicker):
    try:
        payChart = alt.Chart(pd.DataFrame(tickerInfo["companyOfficers"])).mark_bar().encode(
            x=alt.X("totalPay", title="Total Pay"),
            y=alt.Y("title", title="Title"),

        ).properties(height=350, title=selectedTicker).interactive()
    except:
        pass
    if selectedTicker != indexTicker:
        try:
            st.altair_chart(payChart, use_container_width=True)
        except:
            pass
        st.dataframe(data=pd.DataFrame(tickerInfo["companyOfficers"]).style.set_properties(
            **{'text-align': 'center'}), use_container_width=True)
    else:
        st.write("N/A")


def getNews(selectedTicker):
    st.markdown("### News")
    allNews = [news for news in scraper.getNews(
        selectedTicker) if "thumbnail" in news]
    for news in allNews[:5]:
        cols = st.columns([1, 0.1, 4.5, 2])
        with cols[0]:
            st.write("")
            try:
                st.image(news['thumbnail']['resolutions'][1]['url'])
            except:
                st.image(news['thumbnail']['resolutions'][0]['url'])
        with cols[2]:
            st.markdown(f"##### {news['title']}")
            st.write(news['publisher'])
        with cols[3]:
            st.write("")
            st.write("")
            if st.button("More >", key=news['link']):
                webbrowser.open_new_tab(news['link'])


def getIndustryTab(ticker, selectedIndex):
    indexTicker, df = scraper.getSymbols(selectedIndex)
    df = df.reset_index()
    industry = df[df["Symbol"] == ticker]["GICS Sector"].reset_index(drop=True)[
        0]
    st.subheader(industry)
    pass  # TODO: Add industry comparisons


def getMovingAveragesChart(data, intervalHours):
    st.subheader("Moving Averages")
    cols = st.columns(5)
    with cols[3]:
        shortWindow = st.slider('Window A (Days)', step=intervalHours // 24, min_value=intervalHours * 1 // 24, max_value=intervalHours * 50 // 24, value=intervalHours * 20 // 24)
    with cols[4]:
        longWindow = st.slider('Window B (Days)', step=intervalHours // 24, min_value=intervalHours * 1 // 24, max_value=intervalHours * 50 // 24, value=intervalHours * 40 // 24)
    data['date'] = data['date'].astype(str)
    short_run_ma = data['close'].rolling(window=int(shortWindow * 24 // intervalHours)).mean()
    long_run_ma = data['close'].rolling(window=int(longWindow * 24 // intervalHours)).mean()
    moving_averages = pd.DataFrame({
        'Date': data['date'],
        'Close': data['close'],
        'Moving Average A': short_run_ma,
        'Moving Average B': long_run_ma
    }).dropna()
    melted_data = moving_averages.melt(
        id_vars=['Date', 'Close'], var_name='Moving Average', value_name='Price')
    chart = alt.Chart(melted_data).mark_line().encode(
        x='Date:T',
        y=alt.Y('Price:Q', scale=alt.Scale(zero=False)),
        color='Moving Average:N',
        tooltip=['Date:T', 'Price:Q']
    ).properties(
        height=350,
    ).interactive()
    st.altair_chart(chart, use_container_width=True)


def cleanseDates(dates):
    if (type(dates[0]) == pd.Timestamp):
        return dates
    minLength = min([len(date) for date in dates])
    return pd.Series([date[:minLength] for date in dates])


def getResistSupportChart(df):

    st.subheader("Resistance and Support Lines")
    cols = st.columns(5)
    with cols[3]:
        height = st.slider('Height', min_value=-0.3, max_value=0.30, step=0.05, value=0.0)
    with cols[4]:
        width = st.slider('Width', min_value=0.0, max_value=0.50, step=0.05, value=0.25)
    support, resistance = calculate_support_resistance(df, width, height)

    # Create DataFrame for plotting
    df["support"] = support
    df["resistance"] = resistance
    df["date"] = pd.to_datetime(df['date'], utc=True)
    # Plot the data using Altair
    lineChart = alt.Chart(df).mark_line().encode(
        x=alt.X("date", title="Date"),
        y=alt.Y('close', scale=alt.Scale(zero=False), title="Close"),
        color=alt.value("green")
    )
    lineChart += alt.Chart(df).mark_line().encode(
        x=alt.X("date", title="Date"),
        y=alt.Y('resistance', title="Resistance"),
        color=alt.value("red"),
    )
    lineChart += alt.Chart(df).mark_line().encode(
        x=alt.X("date", title="Date"),
        y=alt.Y('support', title="Support"),
        color=alt.value("blue"),
    )

    st.altair_chart(lineChart.properties(
        height=350).interactive(), use_container_width=True)
    


def calculate_support_resistance(data, width, height):
    # print("calculating")
    data["date"] = pd.to_datetime(cleanseDates(data['date']), utc=True)
    # gets rid of wiggly lines due to missing timestamps
    x = data['date'].apply(lambda c: int(c.timestamp()))
    y = data['close']
    p = np.polyfit(x, y, 1)  # Perform linear regression
    #print("polyfit", p)
    regression_line = np.polyval(p, x)
    support_line = regression_line - (np.max(y) - np.min(y)) * width + (np.max(y) - np.min(y)) * height
    # Add the range to support line to get resistance line
    resistance_line = regression_line + (np.max(y) - np.min(y)) * width + (np.max(y) - np.min(y)) * height
    # print("RESULT")
    #print(support_line, resistance_line)
    return support_line, resistance_line


def getMomentumChart(df):
    momentum_window = 10  # Specify the window size for momentum calculation
    df = calculate_momentum(df, momentum_window)
    chart = alt.Chart(df).mark_line().encode(
        x=alt.X("date", title="Date"),
        y=alt.Y('momentum:Q', title="Momentum",),

    )
    zero_line = alt.Chart(pd.DataFrame({'y': [0]})).mark_rule(color='red', strokeDash=[7, 7], size=3).encode(
        y='y:Q'
    )
    chart += zero_line 
    

    st.subheader("Momentum")
    st.altair_chart(chart.properties(
        height=350
    ).interactive(), use_container_width=True)


def calculate_momentum(data, window):
    data['momentum'] = data['close'].pct_change(window) * 100
    return data.dropna()
