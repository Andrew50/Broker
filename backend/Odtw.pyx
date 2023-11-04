import numpy as np
cimport numpy as np
from libc.math cimport sqrt

class Odtw:
    def calcBounds(np.ndarray[double, ndim=1] x, np.ndarray[double, ndim=1] upper, np.ndarray[double, ndim=1] lower):
        cdef int bars = len(x)
        cdef int i 
        cdef double totalLowerBound = 0.0
        cdef int start = bars - (bars // 4)
        for i in range(start, bars):
            if x[i] > upper[i] or x[i] < lower[i]:
                return 99
        for i in range(start):
            if x[i] > upper[i]:
                totalLowerBound += (x[i] - upper[i]) ** 2
            elif x[i] < lower[i]:
                totalLowerBound +=(x[i] - lower[i]) ** 2
        return sqrt(totalLowerBound) * 100
