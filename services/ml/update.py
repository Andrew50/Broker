from data import Data
from datetime import datetime, time
import pytz
import numpy as np
import pandas as pd

import psycopg2
import yfinance as yf


    #self.cache = redis.Redis(host=cache_host, port=6379)

conn = psycopg2.connect(host='localhost',port='5432',user='postgres',password='pass')



#with conn.cursor() as cursor:
#    cursor.execute("SELECT * FROM tickers;")
#    tickers = cursor.fetchall()
#    print(tickers)
def format_datetime(dt,reverse=False):
    if reverse:
        return datetime.datetime.fromtimestamp(dt)
    if type(dt) == int or type(dt) == float or type(dt) == np.int64 or type(dt) == np.float64:
        return dt
    if dt is None or dt == '': return None
    if dt == 'current': return datetime.datetime.now(pytz.timezone('EST'))
    if isinstance(dt, str):
        try: dt = datetime.datetime.strptime(dt, '%Y-%m-%d')
        except: dt = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
    time = datetime.time(dt.hour, dt.minute, 0)
    dt = datetime.datetime.combine(dt.date(), time)
    if dt.hour == 0 and dt.minute == 0:
        time = datetime.time(9, 30, 0)
        dt = datetime.datetime.combine(dt.date(), time)
    dt = dt.timestamp()
    return dt

def findex(df, dt):
    dt = format_datetime(dt)
    i = int(len(df)/2)      
    k = int(i/2)
    while k != 0:
        #date = df.index[i]
        date = df[i,0]
        if date > dt:
            i -= k
        elif date < dt:
            i += k
        k = int(k/2)
    while df[i,0] < dt:
        i += 1
    while df[i,0] > dt:
        i -= 1
        if i < 0:
            raise TimeoutError
    return i

def is_market_open(pm = False):

    dt = datetime.now(pytz.timezone('US/Eastern'))
    if (dt.weekday() >= 5):
        return False
    hour = dt.hour
    minute = dt.minute
    if pm:
        if hour >= 16 or hour < 4:
            return False
        return True
    else:
        if hour >= 10 and hour <= 16:
            return True
        elif hour == 9 and minute >= 30:
            return True
        return False

market_open = time(9, 30)
market_close = time(16, 0)
with conn.cursor() as cursor:
    tickers = [[1, 'AAPL'] , [2, 'MSFT']]
    for ticker_id, ticker in tickers:
        df = yf.download(tickers = ticker, period = '5d', group_by='ticker', interval = '1m', ignore_tz = True, auto_adjust=True, progress=False, show_errors = False, threads = True, prepost = True) 
        df.dropna(inplace = True)
        if df.empty:
            continue
        #df.index = df.index + pd.Timedelta(minutes = 570)
        df = df.reset_index().to_numpy()
        np.set_printoptions(threshold=np.inf)
        #print(df[:,0])
        if is_market_open(pm = True):
            df = df[:-1]
        cursor.execute('SELECT EXTRACT(EPOCH FROM MAX(t)) FROM quotes_1_extended WHERE ticker_id = %s;', (ticker_id,))
        last_timestamp = cursor.fetchone()[0]
        if False: #last_timestamp is not None:
            index = findex(df, last_timestamp) 
            df = df[index + 1:,:]

        df = [(ticker_id, row[0].time() >= market_open and row[0].time() < market_close, row[0], row[1], row[2], row[3], row[4], row[5]
            ) for row in df.tolist()]

        insert_query = """
        INSERT INTO quotes_1_extended (ticker_id, extended_hours, t, open, high, low, close, volume) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (ticker_id, t) DO UPDATE 
        SET open = EXCLUDED.open, 
            high = EXCLUDED.high, 
            low = EXCLUDED.low, 
            close = EXCLUDED.close, 
            volume = EXCLUDED.volume
        """
        cursor.executemany(insert_query, df)
        conn.commit()

