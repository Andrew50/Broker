import numpy as np
import matplotlib.pyplot as plt
from sync_Data import Data

NUM_BARS = 25
SMOOTHING_FACTOR = 12



def normalize(x):
    mean = np.mean(x)
    std = np.std(x)
    x = (x - mean) / std

    return x

def min_max(x): 
    x = (x - np.min(x)) / (np.max(x) - np.min(x))
    return x
    
def smooth(x):
    l = NUM_BARS // SMOOTHING_FACTOR
    window = np.ones(l) / l
    x = np.convolve(x, window, mode='same')
    return x

def compare(data,ticker1,dt1,ticker2,dt2,ticker3,dt3):
    x = data.get_df('raw',ticker1,'1d',dt1, bars=NUM_BARS)
    y = data.get_df('raw',ticker2,'1d',dt2, bars=NUM_BARS)
    z = data.get_df('raw',ticker3,'1d',dt3, bars=NUM_BARS)

    
    time = range(len(x))
    if False:
        for i in range(x.shape[1]):
            plt.scatter(time, x[:, i], label=f'x{i}',c='b')
            plt.scatter(time, y[:, i], label=f'y{i}',c='r')
    else:
        print(x)
        #x = x[:,4]
        #y = y[:,4]
        #z = z[:,4]
        x = np.mean(x[:,1:4],axis=1)
        y = np.mean(y[:,1:4],axis=1)
        z = np.mean(z[:,1:4],axis=1)
        x, y, z = normalize(x), normalize(y), normalize(z)
        #x, y = min_max(x), min_max(y)
        x, y, z = smooth(x), smooth(y), smooth(z)
        plt.scatter(time, x, label=ticker1)
        plt.scatter(time, y, label=ticker2)
        plt.scatter(time, z, label=ticker3)
        
    plt.xlabel('Time')
    plt.ylabel('Value')
    plt.legend()
    plt.show()
    
   
    #distance[0][1] = str(data.format_datetime(dt=distance[0][1], reverse=True))
 
ticker1, dt1 = 'MRK', '2022-11-17'
ticker3, dt3 = 'EGY','2022-02-28'
ticker2, dt2 = 'JBBB', '2023-07-13'
compare(Data(),ticker1,dt1,ticker2,dt2,ticker3,dt3)