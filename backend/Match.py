import os, sys
from locale import normalize
from multiprocessing.pool import Pool
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
    `
    def run(ds,y):
        
        radius = math.ceil(np_bars/10)
        upper, lower = Odtw.calcBounds(y, radius)
        cutoff = 0.02*100
        arglist = [[x, y, tick, index, upper, lower, cutoff, radius, np_bars] for x, tick, index in ds]
        start = datetime.datetime.now()
        scores = Pool().map(Match.worker, arglist)#Main.pool(Match.worker, arglist)
        print(f'completed in {datetime.datetime.now() - start}')
        print(f'average time is {(datetime.datetime.now()-start)/len(scores)}')
        scores = list(filter(lambda x : x is not None, scores))
        scores.sort(key=lambda x: x[0])
        print(f"Total: {len(scores)}")
        return scores[:20]

    def worker(bar):
        x, y, ticker, index, upper, lower, cutoff, radius, num_bars = bar
        
        if (Odtw.calclowerBound(x, upper, lower, num_bars) > cutoff): return None
        return [Odtw.dtwupd(x,y,radius), ticker, index]

    def compute(db,ticker,dt,tf):
        dt = Database.format_datetime(dt)
        y = Data(db,ticker, tf, dt,bars = np_bars+1).df###################
        ds = Dataset(db,'full').dfs
        top_scores = Match.run(ds, y)
        formatted_top_scores = []
        for score, ticker, index in top_scores:
            formatted_top_scores.append([ticker,str(Data(ticker).df.index[index]),round(score,2)])
        return formatted_top_scores

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
    
