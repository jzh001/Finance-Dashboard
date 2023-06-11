import streamlit as st
import finance_data_scraper as scraper
import altair as alt
import webbrowser
import pandas as pd
import numpy as np
from datetime import datetime


def getSideBar(selectedIndex):
    if selectedIndex != 'Custom':
        indexTicker, symbols = scraper.getSymbols(selectedIndex)

        # List of options for the dropdown
        symbolOptions = [indexTicker] + symbols["Symbol"].tolist()

        # Dropdown component
        selectedTicker = st.sidebar.selectbox(
            "Ticker", symbolOptions, index=symbolOptions.index(indexTicker), key="indexTicker")

    else:
        selectedTicker = st.sidebar.text_input(
            "Custom Ticker", max_chars=7, value="AAPL")
        indexTicker = "Custom"

    duration = st.sidebar.selectbox(
        "Duration", ["1d", "5d", "1wk", "1mo", "3mo", "6mo", "YTD", "1y", "5y", "10y"], index=7, key="duration")

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
    # cols = st.columns(6)
    # with cols[-1]:
    #     use_log_scale = st.checkbox('Use Logarithmic Scale')
    lineChart = alt.Chart(data).mark_line(size=2).encode(
        x=alt.X("date", title="Date"),
        y=alt.Y('close', scale=alt.Scale(zero=False,
                                         # type='linear' if not use_log_scale else 'log'
                                         ),
                title="Close")
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
    ).properties(height=170).interactive()
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
        shortWindow = st.slider('Window A (Days)', step=intervalHours // 24, min_value=intervalHours *
                                1 // 24, max_value=intervalHours * 50 // 24, value=intervalHours * 20 // 24)
    with cols[4]:
        longWindow = st.slider('Window B (Days)', step=intervalHours // 24, min_value=intervalHours *
                               1 // 24, max_value=intervalHours * 50 // 24, value=intervalHours * 40 // 24)
    data['date'] = data['date'].astype(str)
    short_run_ma = data['close'].rolling(
        window=int(shortWindow * 24 // intervalHours)).mean()
    long_run_ma = data['close'].rolling(
        window=int(longWindow * 24 // intervalHours)).mean()
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
    try:
        minLength = min([len(date) for date in dates])
    except:
        return dates
    return pd.Series([date[:minLength] for date in dates])


def getResistSupportChart(df):

    st.subheader("Resistance and Support Lines")
    cols = st.columns(5)
    with cols[3]:
        height = st.slider('Height', min_value=-0.3,
                           max_value=0.30, step=0.05, value=0.0)
    with cols[4]:
        width = st.slider('Width', min_value=0.0,
                          max_value=0.50, step=0.05, value=0.25)
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
    # print("polyfit", p)
    regression_line = np.polyval(p, x)
    support_line = regression_line - \
        (np.max(y) - np.min(y)) * width + (np.max(y) - np.min(y)) * height
    # Add the range to support line to get resistance line
    resistance_line = regression_line + \
        (np.max(y) - np.min(y)) * width + (np.max(y) - np.min(y)) * height
    # print("RESULT")
    # print(support_line, resistance_line)
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


def getInterestChart(df):
    chart = alt.Chart(df).mark_line(size=2).encode(
        x=alt.X("end_of_day", title="End of Day"),
        y=alt.Y('sora', title="SORA")
    ).properties(height=400, title="MAS Interest Rate").interactive()
    st.altair_chart(chart, use_container_width=True)


def getExchangeRateChart(df, id):
    cols = st.columns(6)
    with cols[-1]:
        currencySelected = st.selectbox(
            "Select Currency", options=df.columns[1:], key="currency_" + id)
    chart = alt.Chart(df).mark_line(size=2).encode(
        x=alt.X("end_of_week", title="End of Week"),
        y=alt.Y(currencySelected, title="Exchange Rate")
    ).properties(height=400, title="MAS Exchange Rate").interactive()
    st.altair_chart(chart, use_container_width=True)


def getDataTab(stockData, interestData):
    st.subheader("Stocks")
    st.dataframe(data=stockData[::-1].reset_index(drop=True).style.set_properties(
        **{'text-align': 'center'}), use_container_width=True, height=250)
    if len(interestData) != 0:
        st.subheader("Interest Rate")
        st.dataframe(data=interestData[::-1].reset_index(drop=True).style.set_properties(
            **{'text-align': 'center'}), use_container_width=True, height=250)

def getMacroChartsTab(interestData, exchangeData, duration, id):
    if scraper.convertDurationToHours("1wk") > scraper.convertDurationToHours(duration) or len(interestData) == 0 or len(exchangeData) == 0:
        return
    
    interestTab, exchangeTab = st.tabs(["Interest Rate", "Exchange Rate"])
    with interestTab:
        getInterestChart(interestData)
    with exchangeTab:
        getExchangeRateChart(exchangeData, id)

def getEconomyTab(stockData, interestData, exchangeData, duration):
    if scraper.convertDurationToHours("1wk") > scraper.convertDurationToHours(duration) or len(interestData) == 0 or len(exchangeData) == 0:
        return
    mergedDf = mergeData(stockData[["date", "close"]], "date", interestData[["end_of_day", "sora"]], "end_of_day")
    df = pd.DataFrame({'Date': mergedDf['date'],'Close': mergedDf['close'], "Interest Rate": mergedDf['sora']})
    df['Date'] = pd.to_datetime(df['Date'])
    # getMacroChartsTab(interestData, exchangeData, duration,"economyTab")
    getCorrelationLine(df)
    getCloseInterestScatter(df)

def getCorrelationLine(df):
    
    # Create an Altair scatter plot
    
    scatter_plot = alt.Chart(df).mark_circle(size=70).encode(
        x='Date:T',
        y=alt.Y('Close:Q', scale=alt.Scale(zero=False)),
        color=alt.Color('Interest Rate:Q', scale=alt.Scale(scheme='viridis'))
    )
    line_graph = alt.Chart(df).mark_line(size=0.3).encode(
        x='Date:T',
        y=alt.Y('Close:Q', scale=alt.Scale(zero=False)),
    )
    chart = scatter_plot + line_graph
    chart = chart.properties(
        height=400
    ).interactive()

    # Display the scatter plot using Streamlit
    st.write("Closing Prices and Interest Rate")
    st.altair_chart(chart, use_container_width=True)

def getCloseInterestScatter(df):
    scatter_plot = alt.Chart(df).mark_circle().encode(
        x=alt.X('Interest Rate:Q', scale=alt.Scale(zero=False)),
        y=alt.Y('Close:Q', scale=alt.Scale(zero=False)),
    ).properties(
        height=400
    ).interactive()
    st.altair_chart(scatter_plot, use_container_width=True)

def mergeData(df1, col1, df2, col2): #df1 > df2
    df1[col1] = pd.to_datetime(df1[col1]).dt.tz_localize(None)
    df2[col2]  = pd.to_datetime(df2[col2]).dt.tz_localize(None)
    df1 = df1.set_index(col1)
    df2 = df2.set_index(col2)
    df = pd.merge(df1, df2, left_index=True, right_index=True).reset_index()
    df = df.rename(columns={'index': 'date'})
    return df