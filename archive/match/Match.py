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
from sync_Data import Data

NUM_BARS = 25
CUTOFF = 100*100


class Match: 

   
    def compute(data,ticker,tf,dt):
        ds = data.get_ds(tf=tf,form='match')
        y = data.get_df('match',ticker,tf,dt, bars=NUM_BARS)[:, 2:-1]
        radius = math.ceil(NUM_BARS/10)
        upper, lower = Odtw.calcBounds(y[:, 3], radius)
        start = datetime.datetime.now()
        returns = []
        
        
        for ticker, x in ds:
            returns += heapq.nsmallest(3, Odtw.calcDtw(x, y, upper, lower, NUM_BARS, CUTOFF, radius, ticker), key=lambda x: x[2])
        top_scores = heapq.nsmallest(20, returns, key=lambda x: x[2])
        print(f"time to complete calculation {datetime.datetime.now() - start}")
        #print(top_scores)
        match_data =  [[ticker,str(data.format_datetime(dt=timestamp, reverse=True)),round(score,2)] for ticker,timestamp, score in top_scores]
        for i in range(len(match_data)): match_data[i][1] = match_data[i][1][:10]
        return match_data
    
    def normalize(x):#changed
        mean = np.mean(x)
        std = np.std(x)
        normalized_x = (x - mean) / std
        return normalized_x
    
    def compare(data,ticker,tf,dt,ticker2,dt2):
        y = data.get_df('match',ticker,tf,dt, bars=NUM_BARS)
        x = data.get_df('match',ticker2,tf,dt2, bars=NUM_BARS)#[:, 2:-1]
        x = Match.normalize(x)
        y = Match.normalize(y)
        y = y[:, 2:-1]
        radius = math.ceil(NUM_BARS/10)
        upper, lower = Odtw.calcBounds(y[:, 3], radius)
        distance = Odtw.calcDtw(x, y, upper, lower, NUM_BARS, CUTOFF, radius, ticker2,use_bounds = False)
        #distance[0][1] = str(data.format_datetime(dt=distance[0][1], reverse=True))
        return distance[0][2]
    
def get(data,user_id,ticker,tf,dt):
    return Match.compute(data,ticker,tf,dt)

if __name__ == '__main__':
    #print(get(Data(),None,'CELH','1d','2023-08-10'))
    data = Data()
    ticker, tf, dt = 'MRK', '1d', '2022-11-17'
    #print(Match.compare(data,ticker,tf,dt,'EGY','2022-02-28'))
    #ticker, tf, dt = 'CHGG', '1d', '2021-11-02'
    #print(Match.compare(data,ticker,tf,dt,'PTON','2021-11-05'))
    
    print(get(data,None,ticker,tf,dt))




    # def formatArray(ds, onlyCloseAndVol = True, yValue = False, whichColumn=4):
    #     if yValue:
    #         newDf = np.zeros(len(ds)-1)
    #         for i in range(1, len(ds)):
    #             newDf[i-1] = ds[i, 4]/ds[i-1, 4] - 1
    #         return newDf.flatten()
    #     if onlyCloseAndVol: 
    #         if(len(ds) < 3): return np.zeros((1, 4))
    #         d = np.zeros((len(ds)-1, 4))
    #         for i in range(1, len(ds)):
    #             close = ds[i,whichColumn]
    #             d[i-1] = [float(close), float(close/ds[i-1,whichColumn] - 1), ds[i, 5], ds[i, 0]]
    #         return d
    #     else: 
    #         d = np.zeros((len(ds), 6))
    #         for i in range(len(d)-1):
    #             d[i][0] = ds[i][0]
    #             d[i][1] = float(ds[i+1][1]/ds[i][4] - 1)
    #             d[i][2] = float(ds[i+1][2]/ds[i][4] - 1)
    #             d[i][3] = float(ds[i+1][3]/ds[i][4] - 1)
    #             d[i][4] = float(ds[i+1][4]/ds[i][4] - 1)
    #             d[i][5] = ds[i][5]
            
    #         return d
    #     raise AttributeError
    #     return d 