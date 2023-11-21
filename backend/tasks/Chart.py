import json
import pandas as pd

#try:
#except:
    #from .Data import Data, Database, Cache
    
    #god
from Data import data

def get(args):
    args += ['MSFT','1d',None][len(args):]
    ticker,tf,dt = args
    df = data.get_df('chart',ticker,tf,dt)
    list_of_lists = df.tolist()[:]

    # Convert the first column (Unix timestamps) to string datetimes
    if 'd' in tf or 'w' in tf:
        list_of_lists = [{
        'time': pd.to_datetime(row[0], unit='s').strftime('%Y-%m-%d'),
        'open': row[1],
        'high': row[2],
        'low': row[3],
        'close': row[4]
    } for row in list_of_lists]
    else:
        list_of_lists = [{
        'time': pd.to_datetime(row[0], unit='s').strftime('%Y-%m-%d %H:%M:%S'),
        'open': row[1],
        'high': row[2],
        'low': row[3],
        'close': row[4]
        }for row in list_of_lists]
        #for row in list_of_lists:
          #  row[0] = pd.to_datetime(row[0], unit='s').strftime('%Y-%m-%d %H:%M:%S')
        


    
    r = json.dumps(list_of_lists)
    return r
if __name__ == '__main__':
    print(get('AAPL','1d'))