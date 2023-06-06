import yahooquery as yq
import yfinance as yf
import pandas as pd
import numpy as np
from datetime import datetime, timedelta



def getYahooHistorical(ticker,duration="10y", interval="1mo"):

    ticker = yq.Ticker(ticker)

    # Calculate the start date
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(days=convertIntervalToDays(duration))).strftime("%Y-%m-%d")


    # Retrieve historical data for the past 10 years
    historical_data = ticker.history(start=start_date, end=end_date, interval=interval)

    return historical_data.reset_index(level=0, drop=True).reset_index()


def convertIntervalToDays(interval):
    if interval == "YTD":
        return (datetime.today() - datetime(datetime.now().year, 1, 1)).days
    elif (interval[-1] == "y"):
        return int(interval[:-1]) * 365
    elif (interval[-2:] == "mo"):
        return int(interval[:-2]) * 30
    elif (interval[-2:] == "wk"):
        return int(interval[:-2]) * 7
    elif (interval[-1] == "d"):
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