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
            
        
       
    
