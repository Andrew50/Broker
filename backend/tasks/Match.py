import os, sys
from locale import normalize
from multiprocessing.pool import Pool
from Data import Main, Data, Dataset
import numpy as np
import pandas as pd
import datetime
from Study import Screener as screener
import time
from discordwebhook import Discord
import numpy as np
from sklearn import preprocessing
from sfastdtw import sfastdtw
import mplfinance as mpf
import torch
from tqdm import tqdm
from scipy.spatial.distance import euclidean
from multiprocessing import Pool
from Odtw import Odtw
import math
np_bars = 10

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
        y = y.load_np('dtw',np_bars,True)[0][0]
        radius = math.ceil(np_bars/10)
        upper, lower = Odtw.calcBounds(y, radius)
        cutoff = 0.02*100
        arglist = [[x, y, tick, index, upper, lower, cutoff, radius] for x, tick, index in ds]
        start = datetime.datetime.now()
        scores = Pool().map(Match.worker, arglist)#Main.pool(Match.worker, arglist)
        print(f'completed in {datetime.datetime.now() - start}')
        scores.sort(key=lambda x: x[0])
        count = 0
        total = 0
        for score in scores: 
            total += 1
            if(score[0] == 999):
                count += 1
        print(f"Number of skipped: {count}, Total: {total}")
        return scores[:20]

    def worker(bar):
        x, y, ticker, index, upper, lower, cutoff, radius = bar
        if(Odtw.calclowerBound(x, upper, lower) > cutoff): return [999, ticker, index]
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
    arg = f'{ticker}_{dt}_{tf}'
    top_scores = Match.compute(ticker,dt,tf)
    for score,ticker,date in top_scores:
    #for score, ticker, index in top_scores:
        print(f'{ticker} {date} {score}')


# import os, sys
# src = os.path.dirname(os.path.abspath(__file__))
# parent = src.split('Stocks2')[0]
# sys.path.append(parent + (r'Stocks2/'))
# from locale import normalize
# from multiprocessing.pool import Pool
# from Data import Main, Data, Dataset
# import numpy as np
# import pandas as pd
# import datetime
# from Study import Screener as screener
# import time
# from discordwebhook import Discord
# import numpy as np
# from sklearn import preprocessing
# from sfastdtw import sfastdtw
# import mplfinance as mpf
# import torch
# from tqdm import tqdm
# from sfastdtw import sfastdtw
# from scipy.spatial.distance import euclidean


# np_bars = 20

# class Match:

#     def load(tf):
#         ticker_list = screener.get('full')[:200]
#         df = pd.DataFrame({'ticker': ticker_list})
#         df['dt'] = None
#         df['tf'] = tf
#         ds = Dataset(df)
#         df = ds.load_np('dtw',np_bars)
#         return df

#     def run(ds, ticker, dt, tf):
#         y = Data(ticker, tf, dt,bars = np_bars+1).load_np('dtw',np_bars,True)
#         print(y)
#         y=y[0][0]
#         arglist = [[x, y, tick, index] for x, tick, index in ds]
#         scores = Main.pool(Match.worker, arglist)
#         scores.sort(key=lambda x: x[0])
#         return scores[:20]

#     def worker(bar):
#         x, y, ticker, index = bar
#         distance = sfastdtw(x, y, 1, dist=euclidean)
#         return [distance, ticker, index]

#     def compute(string):
#         ticker,dt,tf = string.split('.')
#         #ticker,dt,tf = lis
#         ds = Match.load(tf)
#         top_scores = Match.run(ds, ticker, dt, tf)
#         formatted_top_scores = []
#         for score, ticker, index in top_scores:
#             formatted_top_scores.append([score,ticker,Data(ticker).df.index[index]])
#         return formatted_top_scores

# if __name__ == '__main__':

#     ticker = 'QQQ'  # input('input ticker: ')
#     dt = '2023-10-03'  # input('input date: ')
#     tf = 'd'  # int(input('input tf: '))
#     arg = ticker + '.' + dt + '.' + tf
#     top_scores = Match.compute(arg)
#     for score,ticker,date in top_scores:
#     #for score, ticker, index in top_scores:
#         print(f'{ticker} {date} {score}')
