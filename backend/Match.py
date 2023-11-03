import os, sys
from locale import normalize
from multiprocessing.pool import Pool
from Data import Database, Data, Dataset
#from Study import Screener as screener
import numpy as np
import json
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
#from Odtw import Odtw
import math
np_bars = 10
sqrt = math.sqrt
class Match:

    def load(tf):
        ticker_list = screener.get('full')[:5000]
        df = pd.DataFrame({'ticker': ticker_list})
        df['dt'] = None
        df['tf'] = tf
        ds = Dataset(df)
        df = ds.load_np('dtw',np_bars)
        return df

    def run(ds, ticker, dt, tf):
        y = Data(ticker, tf, dt,bars = np_bars+1)
        y = y.load_np('dtw',np_bars,True)
        y = y[0][0]
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
        
        if (sqrt(pow(y[0]-x[0], 2) + pow(y[num_bars-1]-x[num_bars-1], 2))*100 > cutoff)or (Odtw.calclowerBound(x, upper, lower, num_bars) > cutoff): return None
        return [Odtw.dtwupd(x,y,radius), ticker, index]

    def compute(ticker,dt,tf):
        dt = Main.format_date(dt)
        #ticker,dt,tf = lis
        ds = Match.load(tf)
        top_scores = Match.run(ds, ticker, dt, tf)
        formatted_top_scores = []
        for score, ticker, index in top_scores:
            formatted_top_scores.append([ticker,str(Data(ticker).df.index[index]),round(score,2)])
        return formatted_top_scores

if __name__ == '__main__':

    ticker = 'JBL'  # input('input ticker: ')
    dt = '2023-10-03'  # input('input date: ')
    tf = 'd'  # int(input('input tf: '))
    top_scores = Match.compute(ticker,dt,tf)
    for score,ticker,date in top_scores:
    #for score, ticker, index in top_scores:
        print(f'{ticker} {date} {score}')
        




import math
from scipy.spatial.distance import euclidean
import numpy as np
sqrt = math.sqrt
# Optimized dynamic time warping for match
# Let y denote the timeseries we want to find similarities of
class Odtw: 
    def calcBounds(y, radius):
        u = np.empty([len(y)])
        l = np.empty([len(y)])
        for i in range(len(y)):
            indexLowerBound = max(0, i-radius)
            indexUpperBound = min(len(y)-1, i+radius)
            u[i] = max(y[indexLowerBound:indexUpperBound+1])
            l[i] = min(y[indexLowerBound:indexUpperBound+1])
        return u, l
    
    def calclowerBound(x, upper, lower, bars):
        for i in range(bars-(bars//4), bars):
            if (x[i] > upper[i]):
                return 99
            elif(x[i] < lower[i]):
                return 99
        totalLowerBound = 0.0
        for i in range(0, bars-(bars//4)):
            if (x[i] > upper[i]):
                totalLowerBound += (x[i]-upper[i])*(x[i]-upper[i])#pow((x[i]-upper[i]), 2)
                continue
            elif(x[i] < lower[i]):
                totalLowerBound += (x[i]-lower[i])*(x[i]-lower[i])#pow((x[i]-lower[i]), 2)
                continue
        return sqrt(totalLowerBound)*100

    def dtwupd(a, b, r):
        """ Compute the DTW distance between 2 time series with a warping band constraint
        :param a: the time series array 1
        :param b: the time series array 2
        :param r: the size of Sakoe-Chiba warping band
        :return: the DTW distance
        """

        m = len(a)
        k = 0

        # Instead of using matrix of size O(m^2) or O(mr), we will reuse two arrays of size O(r)
        cost = [float('inf')] * (2 * r + 1)
        cost_prev = [float('inf')] * (2 * r + 1)
        for i in range(0, m):
            k = max(0, r - i)

            for j in range(max(0, i - r), min(m - 1, i + r) + 1):
                # Initialize all row and column
                if i == 0 and j == 0:
                    c = a[0] - b[0]
                    cost[k] = c * c

                    k += 1
                    continue

                y = float('inf') if j - 1 < 0 or k - 1 < 0 else cost[k - 1]
                x = float('inf') if i < 1 or k > 2 * r - 1 else cost_prev[k + 1]
                z = float('inf') if i < 1 or j < 1 else cost_prev[k]

                # Classic DTW calculation
                d = a[i] - b[j]
                cost[k] = min(x, y, z) + d * d

                k += 1

            # Move current array to previous array
            cost, cost_prev = cost_prev, cost

        # The DTW distance is in the last cell in the matrix of size O(m^2) or at the middle of our array
        k -= 1
        return sqrt(cost_prev[k])*100
            
        
def get(ticker,tf,dt):
    val = table_data = [
    {'id': 1, 'name': 'Alice'},
    {'id': 2, 'name': 'Bob'},
    {'id': 3, 'name': 'Carol'}
]
    #return 'god'
    return json.dumps(val)
    
