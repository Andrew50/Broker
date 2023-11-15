from multiprocessing.pool import Pool
from re import L
from Data import Database, Data, Dataset, Cache
#from Study import Screener as screener
import numpy as np
import json
import math
sqrt = math.sqrt
import datetime


from multiprocessing import Pool
import Odtw
import math
np_bars = 10
num_cores = 3
sqrt = math.sqrt
class Match: 
    
    def run(ds,y): 
        radius = math.ceil(np_bars/10)
        upper, lower = Odtw.calcBounds(y, radius)
        cutoff = 0.02*100
        arglist = [[ds[data], y, data, upper, lower, cutoff, radius] for data in ds]
        start = datetime.datetime.now()
        print('starting match')
        scores = Pool(num_cores).map(Match.worker, arglist)#Main.pool(Match.worker, arglist)
        print(f'completed in {datetime.datetime.now() - start}')
        newScores = []
        start = datetime.datetime.now()
        #DEBUG STARTS HERE
        integ = 0 
        print(f"Number of Tickers Ran: {len(scores)}")
        for tickerScores in scores:
            for i in range(len(tickerScores)):
                newScores.append(tickerScores[i])
                integ = integ + 1
        print(integ)
        newScores.sort(key=lambda x: x[2])
        print('time to sort scores')
        print(datetime.datetime.now() - start)
        return newScores[:20]

    def worker(bar):
        x, y, ticker, upper, lower, cutoff, radius = bar
        if x.ndim != 2: return []
        return Odtw.calcDtw(x, y, upper, lower, np_bars, cutoff, radius, ticker)

    def compute(db,ticker,dt,tf,ds):
        dt = Database.format_datetime(dt)
        y = Data(db,ticker, tf, dt,bars=np_bars+1).df###################
        y = Match.formatArray(y, yValue=True)
        top_scores = Match.run(ds, y)
        formatted_top_scores = []
        for ticker, timestamp, score in top_scores:
            formatted_top_scores.append([ticker,str(Database.format_datetime(timestamp, True)),round(score,2)])
        return formatted_top_scores

    def formatArray(data, onlyCloseAndVol = True, yValue = False, whichColumn=4):
        if yValue:
            d = np.zeros(len(data)-1)
            for i in range(1, len(d)):
                d[i-1] = data[i, 4]/data[i-1, 4] - 1
            d = d[len(d)-np_bars:len(d)].flatten()
            return d
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

    
if __name__ == '__main__':
    
    start = datetime.datetime.now()
    
    cache = Cache()
    ds = cache.get_hash('ds')
    
    db = Database()
    ticker = 'CELH'  # input('input ticker: ')
    dt = '2023-08-10'  # input('input date: ')
    tf = '1d'  # int(input('input tf: '))
    print(Database.format_datetime(dt))
    top_scores = Match.compute(db,ticker,dt,tf,ds)
    for ticker, date, score in top_scores:
    #for score, ticker, index in top_scores:
        print(f'{ticker} {date} {score}')
def get(args):
    start = datetime.datetime.now()
    ticker = args[0]
    dt = args[1]
    tf = args[2]
    db = Database()
    cache = Cache()
    ds = cache.get_hash('ds')
    print(f'data loaded in {datetime.datetime.now() - start}')
    start = datetime.datetime.now()
    match_data = Match.compute(db,ticker,tf,dt, ds)
    print(f'match calculated in {datetime.datetime.now() - start}')
    start = datetime.datetime.now()
    for i in range(len(match_data)):
        match_data[i][1] = match_data[i][1][:10]
    print(f'returned in {datetime.datetime.now() - start}')
    return json.dumps(match_data)
    
