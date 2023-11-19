from re import L
from Data import Data, Dataset, Main
import numpy as np
import json
import math, heapq
sqrt = math.sqrt
import datetime
import Odtw
import math
np_bars = 10
class Match: 
            
    def compute(ds,ticker,tf,dt):
        dt = Main.format_datetime(dt)
        y = Match.formatArray(Data(db,ticker, tf, dt,bars=np_bars+1).df, yValue=True)
        radius = math.ceil(np_bars/10)
        



        upper, lower = Odtw.calcBounds(y, radius)
        cutoff = 0.02*100
        start = datetime.datetime.now()
        returns = []
        for ticker, x in ds.items():
            returns += heapq.nsmallest(2, Odtw.calcDtw(x, y, upper, lower, np_bars, cutoff, radius, ticker), key=lambda x: x[2])
        top_scores = heapq.nsmallest(20, returns, key=lambda x: x[2])
        print(datetime.datetime.now() - start)
        print(top_scores)
        return [[ticker,str(Main.format_datetime(timestamp, True)),round(score,2)] for ticker,timestamp, score in top_scores]
       

    def formatArray(data, onlyCloseAndVol = True, yValue = False, whichColumn=4):
        if yValue:
            newDf = np.zeros(len(data)-1)
            for i in range(1, len(data)):
                newDf[i-1] = data[i, 4]/data[i-1, 4] - 1
            return newDf.flatten()
        if onlyCloseAndVol: 
            if(len(data) < 3): return np.zeros((1, 4))
            d = np.zeros((len(data)-1, 4))
            for i in range(1, len(data)):
                close = data[i,whichColumn]
                d[i-1] = [float(close), float(close/data[i-1,whichColumn] - 1), data[i, 5], data[i, 0]]
            return d
        else: 
            d = np.zeros((len(data), 6))
            for i in range(len(d)-1):
                d[i][0] = data[i][0]
                d[i][1] = float(data[i+1][1]/data[i][4] - 1)
                d[i][2] = float(data[i+1][2]/data[i][4] - 1)
                d[i][3] = float(data[i+1][3]/data[i][4] - 1)
                d[i][4] = float(data[i+1][4]/data[i][4] - 1)
                d[i][5] = data[i][5]
            
            return d
        raise AttributeError
        return d 

def get(args,redis_conn,mysql_conn=None):
    start = datetime.datetime.now()
    ticker = args[0]
    dt = args[2]
    tf = args[1]
 
    ds = Dataset(redis_conn)
    y = Data(redis_conn,ticker)
    match_data = Match.compute(ds,ticker,tf,dt)
    for i in range(len(match_data)):
        match_data[i][1] = match_data[i][1][:10]
    print(datetime.datetime.now() - start)
    return json.dumps(match_data)

if __name__ == '__main__':
    from Database import Cache
    db = Cache()
    print(get(['CELH','1d','2023-08-10'],db))