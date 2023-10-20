import os, sys
src = os.path.dirname(os.path.abspath(__file__))
parent = src.split('Stocks2')[0]
sys.path.append(parent + (r'Stocks2/'))
from locale import normalize
from multiprocessing.pool import Pool
from backend.Data import Main, Data, Dataset
import numpy as np
import pandas as pd
import datetime
from backend.Study import Screener as screener
import time
from discordwebhook import Discord
import numpy as np
from sklearn import preprocessing
from backend.sfastdtw import sfastdtw
import mplfinance as mpf
import torch
from tqdm import tqdm
from backend.sfastdtw import sfastdtw
from scipy.spatial.distance import euclidean


np_bars = 20

class Match:

    def load(tf):
        ticker_list = screener.get('full')[:200]
        df = pd.DataFrame({'ticker': ticker_list})
        df['dt'] = None
        df['tf'] = tf
        ds = Dataset(df)
        df = ds.load_np('dtw',np_bars)
        return df

    def run(ds, ticker, dt, tf):
        y = Data(ticker, tf, dt,bars = np_bars+1).load_np('dtw',np_bars,True)
        y=y[0][0]
        arglist = [[x, y, tick, index] for x, tick, index in ds]
        scores = Main.pool(Match.worker, arglist)
        scores.sort(key=lambda x: x[0])
        return scores[:20]

    def worker(bar):
        x, y, ticker, index = bar
        distance = sfastdtw(x, y, 1, dist=euclidean)
        return [distance, ticker, index]

    def compute(lis):
        ticker,dt,tf = lis
        ds = Match.load(tf)
        top_scores = Match.run(ds, ticker, dt, tf)
        formatted_top_scores = []
        for score, ticker, index in top_scores:
            formatted_top_scores.append([score,ticker,Data(ticker).df.index[index]])
        return formatted_top_scores

if __name__ == '__main__':

    ticker = 'JBL'  # input('input ticker: ')
    dt = '2023-10-03'  # input('input date: ')
    tf = 'd'  # int(input('input tf: '))
    top_scores = Match.compute([ticker,dt,tf])
    for score,ticker,date in top_scores:
    #for score, ticker, index in top_scores:
        print(f'{ticker} {date} {score}')
