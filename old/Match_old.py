from multiprocessing.pool import Pool
from re import L
from Data import Database, Data, Dataset, Cache
#from Study import Screener as screener
import numpy as np
import json
import math, heapq
sqrt = math.sqrt
import datetime


from multiprocessing import Pool
import Odtw, cProfile
import math
np_bars = 10
num_cores = 1#3
sqrt = math.sqrt
class Match: 
    
    def run(ds,y): 
        radius = math.ceil(np_bars/10)
        upper, lower = Odtw.calcBounds(y, radius)
        cutoff = 0.02*100
        


        # start = datetime.datetime.now()
        # min_heap = []  # Min-heap to store top 20 values
        # heap_size = 20  # Define the size of the heap

        # for ticker, x in ds.items():
        #     vals = Odtw.calcDtw(x, y, upper, lower, np_bars, cutoff, radius, ticker)
        #     for val in vals:
        #         if len(min_heap) < heap_size:
        #             heapq.heappush(min_heap, (-val[2], val))  # Push with negative score because heapq is a min-heap
        #         else:
        #             # Replace the largest element if the new element is smaller
        #             if val[2] < -min_heap[0][0]:
        #                 heapq.heapreplace(min_heap, (-val[2], val))

        # top_20 = [heapq.heappop(min_heap)[1] for _ in range(len(min_heap))]
        # top_20.reverse()  # Reverse to get the smallest scores first

        # print(datetime.datetime.now() - start)
        # return top_20




        start = datetime.datetime.now()
        returns = []
        for ticker, x in ds.items():
            vals = Odtw.calcDtw(x, y, upper, lower, np_bars, cutoff, radius, ticker)
            returns += heapq.nsmallest(2, vals, key=lambda x: x[2])
        print(datetime.datetime.now() - start)
        return heapq.nsmallest(20, returns, key=lambda x: x[2])








        
        
        
        # #print(ds)
        
        # #arglist = [[ds[data], y, data, upper, lower, cutoff, radius] for data in ds]
        # batches = 1
        # arglist = [[[],y,upper,lower,cutoff,radius] for _ in range(batches)]
        # i = 0
        # for key, value in ds.items():
        #     arglist[i%batches][0].append([value,key])
        #     i += 1



        # start = datetime.datetime.now()
        # newScores = Match.worker(arglist[0])



        # #for _ in range(5):
        # scores = Pool(num_cores).map(Match.worker, arglist)#, chunksize = 20)#Main.pool(Match.worker, arglist)
       








        print(f'completed in {datetime.datetime.now() - start}')
        newScores = []
        start = datetime.datetime.now()
        #DEBUG STARTS HERE
        integ = 0 
        #print(f"Number of Tickers Ran: {len(scores)}")
        for tickerScores in scores:
            for i in range(len(tickerScores)):
                newScores.append(tickerScores[i])
                integ = integ + 1
        #print(integ)
        return heapq.nsmallest(20, newScores, key=lambda x: x[2])

    def worker(bar):
        
        # xset, y, upper, lower, cutoff, radius = bar
        # top_matches = []  # This will be a heap containing all top matches

        # for x, ticker in xset:
        #     vals = Odtw.calcDtw(x, y, upper, lower, np_bars, cutoff, radius, ticker)

        #     for val in vals:
        #         if len(top_matches) < 2:
        #             heapq.heappush(top_matches, (val[2], val))
        #         else:
        #             # If the heap is full and the current value is smaller than the largest in the heap
        #             if val[2] < top_matches[0][0]:
        #                 heapq.heapreplace(top_matches, (val[2], val))

        # # Convert heap to a sorted list, keeping only the values (discard the sort keys)
        # sorted_top_matches = [val for _, val in sorted(top_matches)]

        # # Now sorted_top_matches contains the top 2 matches from each x,
        # # and you want the overall top 5
        # return heapq.nsmallest(5, sorted_top_matches, key=lambda x: x[2])







        #x, y, ticker, upper, lower, cutoff, radius = bar
        #if x.ndim == 2: return []
        #return Odtw.calcDtw(x, y, upper, lower, np_bars, cutoff, radius, ticker)
        xset, y, upper, lower, cutoff, radius  = bar
        returns = []
        for x, ticker in xset:
            
            #if x.ndim == 2:
            vals = Odtw.calcDtw(x, y, upper, lower, np_bars, cutoff, radius, ticker)
            #if vals:
            #vals.sort(key = lambda x: x[2])
            returns += heapq.nsmallest(2, vals, key=lambda x: x[2])

        return heapq.nsmallest(5, returns, key=lambda x: x[2])
            
    def compute(db,ticker,tf,dt,ds):
        ds = ds
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

def get(args):
    start = datetime.datetime.now()
    ticker = args[0]
    dt = args[1]
    tf = args[2]
    db = Database()
    cache = Cache()
    ds = cache.get_hash('ds')
    #print(f'data loaded in {datetime.datetime.now() - start}')
    start = datetime.datetime.now()
    match_data = Match.compute(db,ticker,tf,dt, ds)
    #print(f'match calculated in {datetime.datetime.now() - start}')
    start = datetime.datetime.now()
    for i in range(len(match_data)):
        match_data[i][1] = match_data[i][1][:10]
    #print(f'returned in {datetime.datetime.now() - start}')
    return json.dumps(match_data)


if __name__ == '__main__':
    print(get(['CELH','2023-08-10','1d']))
    
