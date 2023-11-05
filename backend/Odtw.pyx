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

@cython.boundscheck(False)
@cython.wraparound(False)
def calcDtw(np.ndarray[double, ndim=1] x, np.ndarray[double, ndim=1] y, np.ndarray[double, ndim=1] upper, np.ndarray[double, ndim=1] lower, int bars, double cutoff, int radius):
    cdef int total_length = x.shape[0]
    scores = []
    cdef int n 
    cdef int i 
    with cython.nogil:
        
        for n in range(bars, total_length+1): # for the nth iteration, going through bars n-bars to n-1 
            # Lower Bound Check 
            cdef double totalLowerBound = 0.0
            cdef int start = n - (bars // 4)
            cdef bint terminate = False
            for i in range(start, n):
                if x[i] > upper[i] or x[i] < lower[i]:
                    terminate = True
                    break
            if terminate: continue
            for i in range(n-bars, start):
                if x[i] > upper[i]:
                    totalLowerBound += (x[i] - upper[i]) ** 2
                elif x[i] < lower[i]:
                    totalLowerBound += (x[i] - lower[i]) ** 2
            if(totalLowerBound > cutoff): continue # Check if the lower bound is greater than the cutoff

            # Run full dtw 
            cdef Py_ssize_t i, j, k
            cdef double c, x, y, z, d
             
            # Initialize cost and cost_prev arrays with typed values
            cdef double[:] cost = np.empty(2 * r + 1, dtype=np.float64)
            cdef double[:] cost_prev = np.empty(2 * r + 1, dtype=np.float64)

            # Initialize cost and cost_prev arrays
            for i in range(2 * r + 1):
                cost[i] = float('inf')
                cost_prev[i] = float('inf')

            #cdef double[:] cost = [float('inf')] * (2 * r + 1)
            #cdef double[:] cost_prev = [float('inf')] * (2 * r + 1)

            for i in range(bars):
                k = max(0, r - i)

                for j in range(max(0, i - r), min(bars - 1, i + r) + 1):
                    if i == 0 and j == 0:
                        c = a[0] - b[0]
                        cost[k] = c * c
                        k += 1
                        continue

                    y = float('inf') if j - 1 < 0 or k - 1 < 0 else cost[k - 1]
                    x = float('inf') if i < 1 or k > 2 * r - 1 else cost_prev[k + 1]
                    z = float('inf') if i < 1 or j < 1 else cost_prev[k]

                    d = a[i] - b[j]
                    cost[k] = min(x, y, z) + d * d
                    k += 1

                cost, cost_prev = cost_prev, cost

            k -= 1
            return sqrt(cost_prev[k]) * 100
                

        


@cython.boundscheck(False)
@cython.wraparound(False)
def calclowerBound(np.ndarray[double, ndim=1] x, np.ndarray[double, ndim=1] upper, np.ndarray[double, ndim=1] lower):
    cdef int bars = x.shape[0]
    cdef int i 
    cdef double totalLowerBound = 0.0
    cdef int start = bars - (bars // 4)
    with cython.nogil:
        for i in range(start, bars):
            if x[i] > upper[i] or x[i] < lower[i]:
                with gil:  
                    return 99
        for i in range(start):
            if x[i] > upper[i]:
                totalLowerBound += (x[i] - upper[i]) ** 2
            elif x[i] < lower[i]:
                totalLowerBound +=(x[i] - lower[i]) ** 2
    return sqrt(totalLowerBound) * 100
def dtwupd(np.ndarray[double, ndim=1] a, np.ndarray[double, ndim=1] b, int r):
    cdef int m = a.shape[0]
    cdef Py_ssize_t i, j, k
    cdef double c, x, y, z, d

    # Initialize cost and cost_prev arrays with typed values
    cdef double[:] cost = np.empty(2 * r + 1, dtype=np.float64)
    cdef double[:] cost_prev = np.empty(2 * r + 1, dtype=np.float64)

    # Initialize cost and cost_prev arrays
    for i in range(2 * r + 1):
        cost[i] = float('inf')
        cost_prev[i] = float('inf')

    #cdef double[:] cost = [float('inf')] * (2 * r + 1)
    #cdef double[:] cost_prev = [float('inf')] * (2 * r + 1)

    for i in range(m):
        k = max(0, r - i)

        for j in range(max(0, i - r), min(m - 1, i + r) + 1):
            if i == 0 and j == 0:
                c = a[0] - b[0]
                cost[k] = c * c
                k += 1
                continue

            y = float('inf') if j - 1 < 0 or k - 1 < 0 else cost[k - 1]
            x = float('inf') if i < 1 or k > 2 * r - 1 else cost_prev[k + 1]
            z = float('inf') if i < 1 or j < 1 else cost_prev[k]

            d = a[i] - b[j]
            cost[k] = min(x, y, z) + d * d
            k += 1

        cost, cost_prev = cost_prev, cost

    k -= 1
    return sqrt(cost_prev[k]) * 100