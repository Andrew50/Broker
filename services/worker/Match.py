from re import L
import numpy as np
import json
import math, heapq
sqrt = math.sqrt
import datetime 
import Odtw
import math
import asyncio
import time #temp import
np_bars = 10
from sync_Data import Data


class Match: 
            
    def compute(data,ds,y):
        radius = math.ceil(np_bars/10)
        upper, lower = Odtw.calcBounds(y[:, 3], radius)
        cutoff = 100*100
        start = datetime.datetime.now()
        returns = []
        for ticker, x in ds:
            returns += heapq.nsmallest(3, Odtw.calcDtw(x, y, upper, lower, np_bars, cutoff, radius, ticker), key=lambda x: x[2])
        top_scores = heapq.nsmallest(20, returns, key=lambda x: x[2])
        print(f"time to complete match {datetime.datetime.now() - start}")
        #print(top_scores)
        return [[ticker,str(data.format_datetime(dt=timestamp, reverse=True)),round(score,2)] for ticker,timestamp, score in top_scores]
       

    def formatArray(ds, onlyCloseAndVol = True, yValue = False, whichColumn=4):
        if yValue:
            newDf = np.zeros(len(ds)-1)
            for i in range(1, len(ds)):
                newDf[i-1] = ds[i, 4]/ds[i-1, 4] - 1
            return newDf.flatten()
        if onlyCloseAndVol: 
            if(len(ds) < 3): return np.zeros((1, 4))
            d = np.zeros((len(ds)-1, 4))
            for i in range(1, len(ds)):
                close = ds[i,whichColumn]
                d[i-1] = [float(close), float(close/ds[i-1,whichColumn] - 1), ds[i, 5], ds[i, 0]]
            return d
        else: 
            d = np.zeros((len(ds), 6))
            for i in range(len(d)-1):
                d[i][0] = ds[i][0]
                d[i][1] = float(ds[i+1][1]/ds[i][4] - 1)
                d[i][2] = float(ds[i+1][2]/ds[i][4] - 1)
                d[i][3] = float(ds[i+1][3]/ds[i][4] - 1)
                d[i][4] = float(ds[i+1][4]/ds[i][4] - 1)
                d[i][5] = ds[i][5]
            
            return d
        raise AttributeError
        return d 

def get(data,user_id,ticker,tf,dt):
    #asyncio.run(data.init_async_conn())
    
    start = datetime.datetime.now()
    ds = data.get_ds(tf=tf,form='match')
    
    y = data.get_df('match',ticker,tf,dt, bars=np_bars)[:, 2:-1]
    
    match_data = Match.compute(data,ds,y)
    for i in range(len(match_data)): match_data[i][1] = match_data[i][1][:10]
    print(datetime.datetime.now() - start)
    return match_data

if __name__ == '__main__':
    start = datetime.datetime.now()
    print(get(Data(),None,'CELH','1d','2023-08-10'))
    print(f'total time: {datetime.datetime.now() - start}')