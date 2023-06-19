import pandas as pd
import urllib
import json

def getResaleHDBPrices():
    df = pd.read_csv("Resale HDB Prices.csv")
    notOverlapping = True
    offset = 0
    res = []
    step = 5000
    while (notOverlapping):
        url = f'https://data.gov.sg/api/action/datastore_search?resource_id=f1765b54-a209-4718-8d38-a39237f502b3&limit={step}&sort=month%20desc&offset={offset}'
        
        with urllib.request.urlopen (url) as req:
            res += json.loads(req.read())['result']['records']
        #print(type(res[-1]['_id']))
        if res[-1]['_id'] <= len(df):
            notOverlapping = False
        offset += step
    df2 = pd.DataFrame(res).sort_values(by=['_id'])
    df2 = df2[df2['_id'] > len(df)].reset_index(drop=True)

    return pd.concat([df, df2], ignore_index=True, sort=False).drop_duplicates(ignore_index=True)