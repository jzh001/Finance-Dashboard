import yahooquery as yq
import yfinance as yf
import pandas as pd
from datetime import datetime, timedelta
import urllib.request
import json



def getYahooHistorical(ticker,duration):

    ticker = yq.Ticker(ticker)

    noOfHours = convertDurationToHours(duration)
    interval = getIntervalFromHours(noOfHours)
    

    # Calculate the start date
    end_date = datetime.now().strftime("%Y-%m-%d")
    start_date = (datetime.now() - timedelta(hours=noOfHours)).strftime("%Y-%m-%d")


    # Retrieve historical data for the past 10 years
    historical_data = ticker.history(start=start_date, end=end_date, interval=interval)

    return historical_data.reset_index(level=0, drop=True).reset_index()


def getIntervalFromHours(noOfHours):
    if noOfHours <= 24:
        return "5m"
    elif noOfHours <= 7 * 24:
        return "1h"
    elif noOfHours <= 365 * 24:
        return "1d"
    elif noOfHours <= 5 * 365 * 24:
        return "1wk"
    else:
        # return "1mo"
        return "1wk"

def convertDurationToHours(duration):
    if duration == "YTD":
        return (datetime.today() - datetime(datetime.now().year, 1, 1)).days * 24
    elif (duration[-1] == "y"):
        return int(duration[:-1]) * 365 * 24
    elif (duration[-2:] == "mo"):
        return int(duration[:-2]) * 30 * 24
    elif (duration[-2:] == "wk"):
        return int(duration[:-2]) * 7 * 24
    elif (duration[-1] == "d"):
        return int(duration[:-1]) * 24
    elif (duration[-1] == "h"):
        return int(duration[:-1])
    else:
        return 0
    
def getIntervalfromDuration(duration):
    noOfHours = convertDurationToHours(duration)
    interval = getIntervalFromHours(noOfHours)
    return convertDurationToHours(interval)
    


def getSymbols(index):
    if index == "S&P 500":
        return "^GSPC", pd.read_csv("data/S&P500.csv") # https://en.wikipedia.org/wiki/List_of_S%26P_500_companies
    elif index == "STI":
        return "^STI", pd.read_csv("data/STI.csv")
    elif index == "SG REIT":
        return "CLR.SI", pd.read_csv("data/SG_REIT.csv")
    else:
        return None

def getNews(ticker):
    return yf.Ticker(ticker).news

def getInfo(ticker):
    return yf.Ticker(ticker).info

def getFinancialData(ticker):
    return yq.Ticker(ticker).financial_data


def getDividendData(ticker):
    noOfHours = convertDurationToHours("10y")
    df = yq.Ticker(ticker).dividend_history(start=(datetime.now() - timedelta(hours=noOfHours)).strftime("%Y-%m-%d")).reset_index()
    df["dividendPercent"] = [100 * row['dividends'] / getPriceOnDate(row['date'], ticker) for i, row in df.iterrows()]
    return df


def getAverageYearlyPrice(year, ticker):
    return yq.Ticker(ticker).history(start=datetime(year, 1, 1), end=datetime(year, 1, 1) + timedelta(days=365))['close'].mean()


def getDividendDataByYear(ticker, dividendData):
    df = dividendData
    df['date'] = pd.to_datetime(df['date'])
    df = df.groupby(df['date'].dt.year)['dividends'].sum().reset_index()
    df["dividendPercent"] = [100 * row['dividends'] / getAverageYearlyPrice(int(row['date']), ticker) for i, row in df.iterrows()]
    df.reset_index(drop=True)
    df['date'] = pd.to_datetime(df['date'], format='%Y')
    return df

def getPriceOnDate(date, ticker):
    df = yq.Ticker(ticker).history(start=date, end=date + timedelta(days = 7)).reset_index()
    return df['close'][0] 

def getIndustryData(industry):
    pass


def getMASInterestData(duration="1y"):
    return getMASData('9a0bf149-308c-4bd2-832d-76c8e6cb47ed', duration, "end_of_day", "&fields=end_of_day,sora")

def getMASExchangeRateData(duration = "1y"):
    return getMASData('5aa64bc2-d234-43f3-892e-2f587a220f74', duration, "end_of_week").drop(columns=["timestamp", "preliminary"])

def getMASData(resourceID, duration="1y", dateVar = "end_of_day", add = ""):
    #https://secure.mas.gov.sg/api/APIDescPage.aspx?resource_id=9a0bf149-308c-4bd2-832d-76c8e6cb47ed
    noOfHours = convertDurationToHours(duration)
    start_date = (datetime.now() - timedelta(hours=noOfHours)).strftime("%Y-%m-%d")
    ret = []
    for i in range(4):
        url = f'https://eservices.mas.gov.sg/api/action/datastore/search.json?resource_id={resourceID}&limit=1000&offset={i * 1000}&sort={dateVar}%20desc' + add
        print(url)

        with urllib.request.urlopen (url) as req:
            res = list(json.loads(req.read())['result']['records'])
            ret += res
    df = pd.DataFrame(ret)
    df[dateVar] = pd.to_datetime(df[dateVar])
    df = df[df[dateVar] >= start_date]
    return df[::-1].reset_index(drop=True)
    
def getCountryFromIndex(selectedIndex):
    if selectedIndex == "STI" or selectedIndex == "SG REIT":
        return "SG"
    elif selectedIndex == "S&P 500":
        return "USA"
    else:
        return None
    
