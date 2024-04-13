from data import Data
from tqdm import tqdm
from datetime import datetime, time
import pytz
import numpy as np
import pandas as pd
import psycopg2
import yfinance as yf

market_open = time(9, 30, 0)
market_close = time(16, 0, 0)

def setCache(data, df, ticker_id, screenerTensor, screenerKey):
    if screenerTensor is None:
        pass #god

    else:
        if ticker_id in screenerKey:
            index = screenerKey.index(ticker_id)
            base = screenerTensor[index,:,:]


    
    pass

def setData(cursor,ticker_id,data,df):
    if data.is_market_open(pm = True):
        df = df[:-1]
    cursor.execute('SELECT EXTRACT(EPOCH FROM MAX(t)) FROM quotes_1_extended WHERE ticker_id = %s;', (ticker_id,))
    last_timestamp = cursor.fetchone()[0]
    if last_timestamp is not None:
        last_timestamp = int(last_timestamp)
        index = data.findex(df, last_timestamp) 
        df = df[index + 1:,:]
    df = [(ticker_id, row[0].time() >= market_open and row[0].time() < market_close,
    row[0], row[1], row[2], row[3], row[4], row[5]
    ) for row in df.tolist()]
    insert_query = """
    INSERT INTO quotes_1_extended (ticker_id, extended_hours, t, open, high, low, close, volume) 
    VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
    """
    cursor.executemany(insert_query, df)
    data.db.commit()


def update1(data):
    #fetch new data
    #add to db
    #refresh cache
    #refresh aggregates
    screenerTensor = data.cache.get('screener_1d')
    screenerKey = data.cache.get('screener_1d_key')
    tickers = data.getTickers()
    with data.db.cursor() as cursor:
        for ticker_id, ticker in tqdm(tickers):
            df = yf.download(tickers = ticker, period = '5d', group_by='ticker', interval = '1m', ignore_tz = False, auto_adjust=True, progress=False, show_errors = False, threads = True, prepost = True) 
            df.dropna(inplace = True)
            if df.empty:
                continue
            df = df.reset_index().to_numpy()
            np.set_printoptions(threshold=np.inf)
            #setCache(data,df,ticker_id,screenerTensor,screenerKey)
            setData(cursor,ticker_id,data,df)

def update2(data):
    #new tickers?
#clear temp (cahce, any key thats just a uuid)
    data.cache.delete('temp')
#add journals
    query = """
    INSERT INTO journals (user_id, t)
    SELECT u.user_id, date_trunc('day', CURRENT_TIMESTAMP)
    FROM users u
    WHERE NOT EXISTS (
        SELECT 1
        FROM journals j
        WHERE j.user_id = u.user_id
        AND j.t = date_trunc('day', CURRENT_TIMESTAMP)
    )
    """
    with data.db.cursor() as cursor:
        cursor.execute(query)
        data.db.commit()


def update(data, case):
    if case == 1:
        update1(data)
    elif case == 2:
        update2(data)
    else:
        raise ValueError('Invalid case')

if __name__ == '__main__':
    update(Data(False), 1)

