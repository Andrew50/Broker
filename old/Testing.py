import math
sqrt = math.sqrt
import numpy as np
class TestOdtw:
    def worker(bar):
        xSeq, ySeq, ticker, upper, lower, bars, cutoff, r  = bar
        return TestOdtw.calcDtw(xSeq, ySeq, upper, lower, bars, cutoff, r)
    
    def calcDtw(xSeq, ySeq, upper, lower, bars, cutoff, r):
        scores = []
        cost = np.empty(2 * r + 1, dtype=np.float64)
        cost_prev = np.empty(2 * r + 1, dtype=np.float64)
        # Variables for the Lower Bound Check
        totalLowerBound = 0
        total_length = xSeq.shape[0]
        for n in range(bars, total_length): # for the nth iteration, going through bars n-bars to n-1 
            
            if xSeq[n,0]*xSeq[n, 2] < 700000: continue # Filter out low dollar volume days 
            # Lower Bound Check 
            totalLowerBound = 0.0
            zeroIndex = n-bars
            start = n - (bars // 4)
            terminate = False
            for b in range(start, n):
                if xSeq[b, 1] > upper[b-zeroIndex] or xSeq[b, 1] < lower[b-zeroIndex]:
                    terminate = True
                    break
            if terminate: continue
            for b in range(zeroIndex, start):
                if xSeq[b, 1] > upper[b-zeroIndex]:
                    totalLowerBound += (xSeq[b, 1] - upper[b-zeroIndex]) ** 2
                elif xSeq[b, 1] < lower[b-zeroIndex]:
                    totalLowerBound += (xSeq[b, 1] - lower[b-zeroIndex]) ** 2
            if (sqrt(totalLowerBound)*100) > cutoff: continue # Check if the lower bound is greater than the cutoff

            # Run full dtw 
            # in original version, a = x sequence, b = y sequence. 
            k = 0
            # Initialize cost and cost_prev arrays
            for i in range(2 * r + 1):
                cost[i] = float('inf')
                cost_prev[i] = float('inf')

            for i in range(bars):
                k = max(0, r - i)

                for j in range(max(0, i - r), min(bars - 1, i + r) + 1):
                    if i == 0 and j == 0:
                        c = xSeq[zeroIndex, 1] - ySeq[0]
                        cost[k] = c * c
                        k += 1
                        continue

                    y = float('inf') if j - 1 < 0 or k - 1 < 0 else cost[k - 1]
                    x = float('inf') if i < 1 or k > 2 * r - 1 else cost_prev[k + 1]
                    z = float('inf') if i < 1 or j < 1 else cost_prev[k]

                    d = xSeq[i+zeroIndex, 1] - ySeq[j]
                    cost[k] = min(x, y, z) + d * d
                    k += 1

                cost, cost_prev = cost_prev, cost

            k -= 1
            scores.append([ticker, n, sqrt(cost_prev[k]) * 100])
    return scores
  
if __name__ == '__main__':
    '''
    np_bars = 10
    db = Database()
    ticker = 'JBL'
    dt = '2023-10-03'
    tf = '1d'
    y = Data(db,ticker, tf, dt,bars = np_bars+1).df
    y = Match.formatArray(y, yValue=True)
    ticker = 'SUN'
    data = db.get_df(ticker)
    data = Match.formatArray(data)
    radius = math.ceil(np_bars/10)
    upper, lower = Odtw.calcBounds(y, radius)
    bar = [data, y, ticker, upper, lower, 10, 2, radius]
    profiler = cProfile.Profile()
    profiler.enable()
    scores = TestOdtw.calcDtw(data, y, upper, lower, 10, 2, radius)
    profiler.disable()
    profiler.print_stats(sort='cumulative')'''
    num_cores = 3
    tickerBatches = [ [[], []] for i in range(num_cores) ]
    print(tickerBatches[0])
    '''scores = Match.worker(bar)
    print(datetime.datetime.now()-sTime)
    scores = scores[1]
    scores.sort(key=lambda x: x[1])
    print(scores)'''
