
import numpy as np
from scipy.spatial.distance import euclidean
from scipy.signal import savgol_filter
from sync_Data import Data

BARS = 50
POLY_ORDER = 3
SMOOTHING_WINDOW = BARS // 7 #might need to be odd number

def transform(seq):
    mean = np.mean(seq)
    std = np.std(seq)
    seq = (seq - mean) / std
    seq =  savgol_filter(seq, SMOOTHING_WINDOW,POLY_ORDER, deriv=1)
    #seq =  savgol_filter(seq, SMOOTHING_WINDOW,POLY_ORDER)
    #seq = Keogh EJ, Pazzani MJ (2001) Derivative dynamic time warping. Paper presented at the SIAM International Conference on Data Mining
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
        
def compute_matrix(C):
    N, M = C.shape
    D = np.zeros((N, M))
    D[:, 0] = np.cumsum(C[:, 0])
    D[0, :] = C[0, :]
    for n in range(1, N):
        for m in range(1, M):
            D[n, m] = C[n, m] + min(D[n-1, m], D[n, m-1], D[n-1, m-1])
    return D


def calc(x,y,top_n): #y is query, x is to check
    y, x = transform(y), transform(x)
    M = np.zeros((len(x), len(y)))
    for i in range(len(x)):
        for j in range(len(y)):
            M[i, j] = abs(x[i] - y[j])
    D = compute_matrix(M)
    sorted_indices = np.argsort(D[-1, :])
    
    top_matches = []
    for idx in sorted_indices:
        if all(abs(idx - match['index']) > BARS for match in top_matches):
            P = path(D, m=idx)
            a_ast = P[0, 1]
            b_ast = P[-1, 1]
            cost = D[-1, idx]
            match = {
                'index': b_ast,
                'cost': cost,
            }
            top_matches.append(match)
            if len(top_matches) == top_n:
                break

    return top_matches

data = Data()
tf = '1d'
ticker, dt = 'MRK', '2022-11-17'
ticker2, dt2 = 'EGY','2022-02-28'
x = data.get_df('raw',ticker,tf,dt, bars=BARS)[:,4]
y = data.get_df('raw',ticker2,tf,dt2)

top_matches = calc(x, y[:,4], top_n=50)
for match in top_matches:
    print(data.format_datetime(dt=y[:,0][match['index']], reverse=True) )