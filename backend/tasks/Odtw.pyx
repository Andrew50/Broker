import numpy as np
cimport numpy as np
from libc.math cimport sqrt
cimport cython
@cython.boundscheck(False)
@cython.wraparound(False)
def calcBounds(double[:] y, int radius):
    cdef int n = len(y)
    cdef np.ndarray[double, ndim=1] u = np.empty(n, dtype=np.float64)
    cdef np.ndarray[double, ndim=1] l = np.empty(n, dtype=np.float64)
    cdef Py_ssize_t i

    for i in range(n):
        indexLowerBound = max(0, i - radius)
        indexUpperBound = min(n - 1, i + radius)
        u[i] = max(y[indexLowerBound:indexUpperBound + 1])
        l[i] = min(y[indexLowerBound:indexUpperBound + 1])

    return u, l
# data in format 
#[dt, closePrice, openPriceNormalized, highPriceNormalized, lowPriceNormalized, closePriceNormalized, volume]
@cython.boundscheck(False)
@cython.wraparound(False)
def calcDtw(np.ndarray[double, ndim=2] xSeq, np.ndarray[double, ndim=2] ySeq, np.ndarray[double, ndim=1] upper, np.ndarray[double, ndim=1] lower, int bars, double cutoff, int r, str ticker):
    scores = []
    # Variables for the Lower Bound Check
    cdef int total_length = xSeq.shape[0]
    if total_length < bars: return scores
    cdef Py_ssize_t n = 0
    cdef Py_ssize_t b = 0
    cdef double totalLowerBound = 0
    cdef int zeroIndex = 0
    cdef int start = 0 
    cdef bint terminate = False

    #Variables for full DTW

    cdef Py_ssize_t i, j, k, columnIndexer
    cdef double c, x, y, z, d
    cdef double[:] cost = np.empty(2 * r + 1, dtype=np.float64)
    cdef double[:] cost_prev = np.empty(2 * r + 1, dtype=np.float64)


    for n in range(bars-1, total_length): # for the nth iteration, going through bars n-bars to n-1 
            
        if xSeq[n,1]*xSeq[n, 6] < 800000: continue # Filter out low dollar volume days 
        # Lower Bound Check 
        totalLowerBound = 0.0
        zeroIndex = n-bars+1
        start = n - (bars // 5)
        terminate = False
        for b in range(start, n+1):
            if xSeq[b, 5] > (upper[b-zeroIndex]) or xSeq[b, 5] < (lower[b-zeroIndex]):
                terminate = True
                break
        if terminate: continue
        for b in range(zeroIndex, start):
            if xSeq[b, 5] > upper[b-zeroIndex]:
                totalLowerBound += (xSeq[b, 5] - upper[b-zeroIndex]) ** 2
            elif xSeq[b, 5] < lower[b-zeroIndex]:
                totalLowerBound += (xSeq[b, 5] - lower[b-zeroIndex]) ** 2
        if (sqrt(totalLowerBound)*100) > cutoff: continue # Check if the lower bound is greater than the cutoff

        # Run full dtw 
        # in original version, a = x sequence, b = y sequence. 

        # Initialize cost and cost_prev arrays
        k=0
        for i in range(2 * r + 1):
            cost[i] = float('inf')
            cost_prev[i] = float('inf')

        for i in range(bars):
            k = max(0, r - i)

            for j in range(max(0, i - r), min(bars - 1, i + r) + 1):
                if i == 0 and j == 0:
                    cost[k] = 0
                    for columnIndexer in range(4):
                        c = xSeq[zeroIndex, 2+columnIndexer] - ySeq[0, columnIndexer]
                        cost[k] += c * c
                    k += 1
                    continue

                y = float('inf') if j - 1 < 0 or k - 1 < 0 else cost[k - 1]
                x = float('inf') if i < 1 or k > 2 * r - 1 else cost_prev[k + 1]
                z = float('inf') if i < 1 or j < 1 else cost_prev[k]
                cost[k] = min(x, y, z)
                for columnIndexer in range(4):
                    d = xSeq[i+zeroIndex, 2+columnIndexer] - ySeq[j, columnIndexer]
                    cost[k] += d * d
                k += 1

            cost, cost_prev = cost_prev, cost

        k -= 1
        scores.append([ticker, xSeq[n, 0], sqrt(cost_prev[k]) * 100])
    return scores
                




