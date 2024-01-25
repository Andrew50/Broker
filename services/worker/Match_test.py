

import numpy as np
from sync_Data import Data

NUM_BARS = 25
import matplotlib.pyplot as plt



def normalize(x):
    mean = np.mean(x)
    std = np.std(x)
    x = (x - mean) / std

    return x

def min_max(x): 
    x = (x - np.min(x)) / (np.max(x) - np.min(x))
    return x
    
def smooth(x):
    l = NUM_BARS // 10
    window = np.ones(l) / l
    x = np.convolve(x, window, mode='same')
    return x

def compare(data,ticker,dt,ticker2,dt2):
    y = data.get_df('raw',ticker,'1d',dt, bars=NUM_BARS)
    x = data.get_df('raw',ticker2,'1d',dt2, bars=NUM_BARS)
    
    
    
    
    
    time = range(len(x))
    if False:
        for i in range(x.shape[1]):
            plt.scatter(time, x[:, i], label=f'x{i}',c='b')
            plt.scatter(time, y[:, i], label=f'y{i}',c='r')
    else:
        x = x[:,3]
        y = y[:,3]
        x, y = normalize(x), normalize(y)
        #x, y = min_max(x), min_max(y)
        x, y = smooth(x), smooth(y)
        plt.scatter(time, x, label='x')
        plt.scatter(time, y, label='y')
        
    plt.xlabel('Time')
    plt.ylabel('Value')
    #plt.legend()
    plt.show()
    
   
    #distance[0][1] = str(data.format_datetime(dt=distance[0][1], reverse=True))
 
ticker1, dt1 = 'MRK', '2022-11-17'
#ticker2, dt2 = 'EGY','2022-02-28'
ticker2, dt2 = 'JBBB', '2023-07-13'
compare(Data(),ticker1,dt1,ticker2,dt2)