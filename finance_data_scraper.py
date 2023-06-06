import yahooquery as yq
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta



def getYahooHistorical(ticker,duration):

    ticker = yq.Ticker(ticker)

    noOfHours = convertIntervalToHours(duration)
    interval = ""
    if noOfHours <= 24:
        interval = "5m"
    elif noOfHours <= 5 * 24:
        interval = "1h"
    elif noOfHours <= 365 * 24:
        interval = "1d"
    elif noOfHours <= 5 * 365 * 24:
        interval = "1wk"
    else:
        interval = "1mo"

    # Calculate the start date
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(hours=noOfHours)).strftime("%Y-%m-%d")


    # Retrieve historical data for the past 10 years
    historical_data = ticker.history(start=start_date, end=end_date, interval=interval)

    return historical_data.reset_index(level=0, drop=True).reset_index()


def convertIntervalToHours(interval):
    if interval == "YTD":
        return (datetime.today() - datetime(datetime.now().year, 1, 1)).days * 24
    elif (interval[-1] == "y"):
        return int(interval[:-1]) * 365 * 24
    elif (interval[-2:] == "mo"):
        return int(interval[:-2]) * 30 * 24
    elif (interval[-2:] == "wk"):
        return int(interval[:-2]) * 7 * 24
    elif (interval[-1] == "d"):
        return int(interval[:-1]) * 24
    elif (interval[-1] == "h"):
        return int(interval[:-1])
    else:
        return 0


def getSymbols(index):
    if index == "S&P 500":
        return "^GSPC", pd.read_csv("data/S&P500.csv") # https://en.wikipedia.org/wiki/List_of_S%26P_500_companies
    elif index == "STI":
        return "^STI", pd.read_csv("data/STI.csv")
    elif index == "SG REIT":
        return "^STI", pd.read_csv("data/SG_REIT.csv")
    else:
        return None

def getNews(ticker):
    return yf.Ticker(ticker).news

def getInfo(ticker):
    return yf.Ticker(ticker).info

def getFinancialData(ticker):
    return yq.Ticker(ticker).financial_data


def getDividendData(ticker):
    noOfHours = convertIntervalToHours("10y")
    df = yq.Ticker(ticker).dividend_history(start=(datetime.now() - timedelta(hours=noOfHours)).strftime("%Y-%m-%d")).reset_index()
    df["dividendPercent"] = [100 * row['dividends'] / getPriceOnDate(row['date']) for i, row in df.iterrows()]
    return df

def getPriceOnDate(date):
    df = yq.Ticker("AAPL").history(start=date, end=date + timedelta(days = 7)).reset_index()
    return df['close'][0] 