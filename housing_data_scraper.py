import pandas as pd
import urllib
import json
from datetime import datetime, timedelta

def getResaleHDBPrices():
    df = pd.read_csv("data/Resale HDB Prices.csv")
    notOverlapping = True
    offset = 0
    res = []
    step = 500
    while (notOverlapping):
        url = f'https://data.gov.sg/api/action/datastore_search?resource_id=f1765b54-a209-4718-8d38-a39237f502b3&limit={step}&sort=month%20desc&offset={offset}'
        
        with urllib.request.urlopen (url) as req:
            res += json.loads(req.read())['result']['records']
        #print(type(res[-1]['_id']))
        if res[-1]['_id'] <= len(df):
            notOverlapping = False
        offset += step
        step = 5000
    df2 = pd.DataFrame(res).sort_values(by=['_id'])
    df2 = df2[df2['_id'] > len(df)].reset_index(drop=True)
    final_df = pd.concat([df, df2], ignore_index=True, sort=False).drop_duplicates(ignore_index=True)
    final_df.to_csv("data/Resale HDB Prices.csv", index=False)
    return final_df

def getNMonthsAgo(numMonths = 0):
    target_month = datetime.today() - timedelta(days=30*numMonths)
    return target_month.strftime("%Y-%m")