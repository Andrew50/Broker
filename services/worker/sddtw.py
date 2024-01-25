
import numpy as np
from scipy.spatial.distance import euclidean
from scipy.signal import savgol_filter




BARS = 10
POLY_ORDER = 3
SMOOTHING_WINDOW = BARS // 2 #might need to be odd number

def transform(seq):
    seq =  savgol_filter(seq, SMOOTHING_WINDOW,POLY_ORDER, deriv=1)
    #seq =  savgol_filter(seq, SMOOTHING_WINDOW,POLY_ORDER)
    #seq = Keogh EJ, Pazzani MJ (2001) Derivative dynamic time warping. Paper presented at the SIAM International Conference on Data Mining
    mean = np.mean(seq)
    std = np.std(seq)
    seq = (seq - mean) / std
    return seq

def path(D,m=-1):
    N, M = D.shape
    n = N - 1
    if m < 0:
        m = D[N - 1, :].argmin()
    P = [(n, m)]

    while n > 0:
        if m == 0:
            cell = (n - 1, 0)
        else:
            val = min(D[n-1, m-1], D[n-1, m], D[n, m-1])
            if val == D[n-1, m-1]:
                cell = (n-1, m-1)
            elif val == D[n-1, m]:
                cell = (n-1, m)
            else:
                cell = (n, m-1)
        P.append(cell)
        n, m = cell
    P.reverse()
    P = np.array(P)
    return P
        
def compute_accumulated_cost_matrix_subsequence_dtw(C):
    N, M = C.shape
    D = np.zeros((N, M))
    D[:, 0] = np.cumsum(C[:, 0])
    D[0, :] = C[0, :]
    for n in range(1, N):
        for m in range(1, M):
            D[n, m] = C[n, m] + min(D[n-1, m], D[n, m-1], D[n-1, m-1])
    return D


def calc(x,y): #y is query, x is to check
    y, x = transform(y), transform(x)
    #C = np.abs(np.subtract.outer(y, x))
    M = np.zeros((len(x), len(y)))
    
    # Fill in the cost matrix
    for i in range(len(x)):
        for j in range(len(y)):
            M[i, j] = abs(x[i] - y[j])
    D = compute_accumulated_cost_matrix_subsequence_dtw(M)
    b_ast = D[-1, :].argmin()
    #print('b* =', b_ast)
    #print('Accumulated cost D[N, b*] = ', D[-1, b_ast])
    P = path(D)
    return P, D



y = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11,34,63,34,32,53,45,74,24,123,52,3,21,8,12]
x = [1, 2, 3, 4,5,6,7,8,9,10]

x = x[-BARS:]

p, d = calc(x,y)


print('Optimal warping path P =', p.tolist())
a_ast = p[0, 1]
b_ast = p[-1, 1]
print('a* =', a_ast)
print('b* =', b_ast)
print('Sequence X =', x)
print('Sequence Y =', y)
print('Optimal subsequence Y(a*:b*) =', y[a_ast:b_ast+1])
print('Accumulated cost D[N, b_ast]= ', d[-1, b_ast])
