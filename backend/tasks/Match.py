from multiprocessing.pool import Pool
from Data import Database, Data, Dataset
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
        arglist = [[Match.formatArray(data.df), y, data.ticker, upper, lower, cutoff, radius] for data in ds]
        start = datetime.datetime.now()
        print('starting match')
        print(start)  
        scores = Pool(num_cores).map(Match.worker, arglist)#Main.pool(Match.worker, arglist)
        print(f'completed in {datetime.datetime.now() - start}')
        newScores = []
        start = datetime.datetime.now()
        for tickerScores in scores:
            for i in range(len(tickerScores)):
                newScores.append(tickerScores[i])
        newScores.sort(key=lambda x: x[2])
        print('time to sort scores')
        print(datetime.datetime.now() - start)
        return newScores[:20]

    def worker(bar):
        x, y, ticker, upper, lower, cutoff, radius = bar
        return Odtw.calcDtw(x, y, upper, lower, np_bars, cutoff, radius, ticker)

    def compute(db,ticker,dt,tf):
        dt = Database.format_datetime(dt)
        y = Data(db,ticker, tf, dt,bars = np_bars+1).df###################
        y = Match.formatArray(y, yValue=True)
        
        start = datetime.datetime.now()
        ds = Dataset(db,'full').dfs
        print('time to load dataset:')
        print(datetime.datetime.now()-start)
        
        
        top_scores = Match.run(ds, y)
        formatted_top_scores = []
        for ticker, timestamp, score in top_scores:
            formatted_top_scores.append([ticker,str(Database.format_datetime(timestamp, True)),round(score,2)])
        return formatted_top_scores

    def formatArray(data, onlyCloseAndVol = True, yValue = False):
        data = np.array(data)
        if yValue:
            d = np.zeros((len(data), 1))
            for i in range(len(d)-1):
                d[i] = data[i+1, 4]/data[i, 4] - 1
            d = d[len(d)-1-np_bars:len(d)-1].flatten()
            return d
        if onlyCloseAndVol: 
            if(len(data) < 3): return np.zeros((1, 4))
            d = np.zeros((len(data)-1, 4))
            for i in range(1, len(data)):
                close = data[i,4]
                d[i-1] = [float(close), float(close/data[i-1,4] - 1), data[i, 5], data[i, 0]]
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
    print(start)
    db = Database()
    ticker = 'JBL'  # input('input ticker: ')
    dt = '2023-10-03'  # input('input date: ')
    tf = '1d'  # int(input('input tf: '))
    
    top_scores = Match.compute(db,ticker,dt,tf)
    for ticker, date, score in top_scores:
    #for score, ticker, index in top_scores:
        print(f'{ticker} {date} {score}')
         
        
def get(args):
    ticker = args[0]
    dt = args[1]
    tf = args[2]
    db = Database()
    return json.dumps(Match.compute(db,ticker,tf,dt))
    
