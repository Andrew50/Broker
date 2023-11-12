import time
from multiprocessing import Pool, current_process
import pandas as pd
from Scan import Scan as scan

import yfinance as yf
from Data7 import Data as data
import datetime
from Plot import Plot as plot
from tensorflow.keras.models import load_model








df = pd.read_feather('C:/Screener/sync/database/laptop_h_F.feather')
#pd.read_feather('C:/Screener/sync/database/laptop_F.feather')
print(df)

'''
import os
path = 'C:/Screener/sync/database/'
lis = os.listdir(path)
for p in lis:
    df = pd.read_feather(path + p)
    df['req'] = 0
    print(df)
    df.to_feather(path+p)
###########dont delete
'''
'''
df = pd.read_feather('C:/Screener/sync/full_ticker_list.feather')


i = 0
ii = 0

size = 50
while True:

    df2 = df[i:i + size].reset_index(drop = True)
    df2.to_feather('C:/Screener/tmp/subtickerlists/' + str(ii) + '.feather')

    ii += 1
    i += size


    if i >= len(df):
        break

'''

'''

df = data.get('NGL')
print(df)




#df1 = pd.read_feather('C:/Screener/setups/database/F2.feather')
#df2 = pd.read_feather('C:/Screener/setups/database/FB.feather')
#df3 = pd.read_feather('C:/Screener/setups/database/NF.feather')
#df4 = pd.read_feather('C:/Screener/setups/database/NFB.feather')

#df = pd.DataFrame()
#df['ticker'] = df1['ticker']
#df['date'] = df1['date']
#df['setup'] = df1['setup']  + df3['setup'] + df2['setup'] + df4['setup']

    
#df.to_feather('C:/Screener/setups/database/F.feather')


#df = data.get('yang')

#print(df)



setuptype = 'MR'
################dont delte!!!!!!~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
setups = pd.read_feather('C:/Screener/sync/setups.feather')
setups2 = pd.read_feather('C:/Screener/sync/allsetups.feather')

print(setups)

#ep = setups[setups['Setup'] == 'EP'].reset_index(drop = True)


ep = setups2[setups2['Setup'] == setuptype].reset_index(drop = True)


#ep = pd.concat([ep,ep2]).reset_index(drop = True)

other = setups[setups['Setup'] != setuptype].reset_index(drop = True)


ep['setup'] = 1

other['setup'] = 0


df = pd.concat([ep,other]).sample(frac = 1).reset_index(drop = True)



setups = pd.DataFrame()

setups['ticker'] = df['Ticker']

setups['date'] = df['Date']

setups ['setup'] = df['setup']

print(setups)


gud = setups[setups['setup'] == 1].reset_index(drop = True)
print(len(gud))

setups.to_feather('C:/Screener/setups/' + setuptype + '.feather')


'''








