import os, sys
from locale import normalize
from multiprocessing.pool import Pool
from unittest import defaultTestLoader
from Data import Database, Data, Dataset
#from Study import Screener as screener
import numpy as np
import json
import math
from scipy.spatial.distance import euclidean
import numpy as np
sqrt = math.sqrt
import pandas as pd
import datetime

import time
from discordwebhook import Discord
import numpy as np
from sklearn import preprocessing

import mplfinance as mpf
import torch
from tqdm import tqdm
from scipy.spatial.distance import euclidean
from multiprocessing import Pool
import Odtw
import math
np_bars = 10
sqrt = math.sqrt
class Match: 

    # def load(tf):
    #     ticker_list = screener.get('full')[:5000]
    #     df = pd.DataFrame({'ticker': ticker_list})
    #     df['dt'] = None
    #     df['tf'] = tf
    #     ds = Dataset(df)
    #     df = ds.load_np('dtw',np_bars)
    #     return df

    def run(ds,y):
        
        radius = math.ceil(np_bars/10)
        upper, lower = Odtw.calcBounds(y, radius)
        cutoff = 0.02*100
        arglist = [[x, y, tick, index, upper, lower, cutoff, radius] for x, tick, index in ds]
        start = datetime.datetime.now()
        scores = Pool().map(Match.worker, arglist)#Main.pool(Match.worker, arglist)
        print(f'completed in {datetime.datetime.now() - start}')
        print(f'average time is {(datetime.datetime.now()-start)/len(scores)}')
        scores = list(filter(lambda x : x is not None, scores))
        scores.sort(key=lambda x: x[0])
        print(f"Total: {len(scores)}")
        return scores[:20]

    def worker(bar):
        x, y, ticker, index, upper, lower, cutoff, radius = bar
        
        if (Odtw.calclowerBound(x, upper, lower) > cutoff): return None
        return [Odtw.dtwupd(x,y,radius), ticker, index]

    def compute(db,ticker,dt,tf):
        dt = Database.format_datetime(dt)
        #ticker,dt,tf = lis
        #ds = Match.load(tf)
        y = Data(db,ticker, tf, dt,bars = np_bars+1).df
        ds = Dataset(db,'full').dfs
        y = y[len(y)-1-np_bars:len(y)-1]
        print(y)
        print(len(y))
        raise AttributeError
        #y = y.load_np('dtw',np_bars,True)
        #y = y[0][0]
        top_scores = Match.run(ds, y)
        formatted_top_scores = []
        for score, ticker, index in top_scores:
            formatted_top_scores.append([ticker,str(Data(ticker).df.index[index]),round(score,2)])
        return formatted_top_scores

    def formatArray(data):
        d = np.zeros((data.shape[0]-1, data.shape[1]))
        for i in range(len(d)):
            d[i] = float(data[i+1]/data[i, 3] - 1)
        return d

        
if __name__ == '__main__':
    db = Database()
    ticker = 'AAPL'  # input('input ticker: ')
    dt = None#'2023-10-03'  # input('input date: ')
    tf = '1d'  # int(input('input tf: '))
    
    top_scores = Match.compute(db,ticker,dt,tf)
    for score,ticker,date in top_scores:
    #for score, ticker, index in top_scores:
        print(f'{ticker} {date} {score}')
         
        
def get(ticker,tf,dt):
    db = Database()
    return json.dumps(Match.run(db,ticker,tf,dt))
    
