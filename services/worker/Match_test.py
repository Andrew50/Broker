

import numpy as np
from sync_Data import Data

NUM_BARS = 25
import matplotlib.pyplot as plt



def normalize(x):
    mean = np.mean(x)
    std = np.std(x)
    x = (x - mean) / std

    return x

def compare(data,ticker,dt,ticker2,dt2):
    y = data.get_df('match',ticker,'1d',dt, bars=NUM_BARS)[:, 2:-1]
    x = data.get_df('match',ticker2,'1d',dt2, bars=NUM_BARS)[:, 2:-1]
    
    
    #x = normalize(x)
    #y = normalize(y)
    x = x[:,3]
    y = y[:,3]
   
    time = range(len(x))
    # for i in range(x.shape[1]):
    #     plt.scatter(time, x[:, i], label=f'x{i}',c='b')
    #     plt.scatter(time, y[:, i], label=f'y{i}',c='r')
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