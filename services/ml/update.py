from tqdm import tqdm
from data import Data
import time, numpy as np, yfinance as yf, json, datetime, math
SCREENER_INTERVALS = "1d",

market_open = datetime.time(9, 30, 0)
market_close = datetime.time(16, 0, 0)

def updateCache(data, df, ticker_id, interval, screenerTensor, helper):

    log_1 = helper[ticker]
    key = screenerTensor[:,0,4]
    if ticker_id in key:
        index = screenerTensor.index(ticker_id)
    else:
        raise Exception('man')
    screenerTensor[index,-1,:] = np.array([math.log(x) - log_1 for x in df[-1]])
    return screenerTensor


    """
    if time.now() >= next_update:
        
        new = log
        next_update = df[-1:0] + pd.timedelta(interval)

    else: #update cache
        if ticker_id in screenerKey:
            index = screenerKey.index(ticker_id)
            base = screenerTensor[index,:,:]


    #push to tensor in redis AI at 1d_screener
    #push key to 1d_screener_key
    """


def newCache(data,interval,tickers):
    bars = 100

    if interval != "1d":
        raise Exception("good luck")
    table, bucket, aggregate = data.getQueryInfo(interval, pm)
    ds = []
    key = []
    for ticker_id, ticker in tickers:
        query = ""
        args = [ticker_id]
        if aggregate:
            raise Exception('to code')
        else:
            query = f"""SELECT open, high, low, close, volume
                        FROM {table}
                        WHERE ticker_id = {ticker_id}
                        ORDER BY t DESC
                        LIMIT {bars}"""
        with data.db.cursor() as cursor:
            cursor.execute(query)
            results = cursor.fetchall()
        if len(results) < bars:
            #TODO pad
            continue
        results = np.array(results, dtype=np.float64)
        l = 20
        dolvol = np.mean(results[-l:,4]) * np.mean(results[-l:,3])
        adr = (np.mean((results[-l:,1] / results[-l:,2])) - 1 ) * 100
        mcap = np.inf #TODO
        results = results[:,:5]
        results = np.log(results)
        close = np.roll(results[:,2], shift=1)
        results = results - close[:,np.newaxis]
        results[0,:] = np.array([dolvol,adr,mcap,ticker_id]) 
        ds.append(results[1:])
        #key.append(ticker)
    return np.array(ds)
    #return np.array(ds), np.array(key)

def setQuotes(cursor,ticker_id,data,df):
    if data.is_market_open(pm = True):
        df = df[:-1]
    #cursor.execute('SELECT EXTRACT(EPOCH FROM MAX(t)) FROM quotes_1_extended WHERE ticker_id = %s;', (ticker_id,))
    cursor.execute('SELECT MAX(t) FROM quotes_1_extended WHERE ticker_id = %s;', (ticker_id,))
    last_timestamp = cursor.fetchone()[0]
    if last_timestamp is not None:
        #last_timestamp = int(last_timestamp)
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

def dayUpdate(data):
    tickers = data.getTickers()
    cacheDataDict = {}
    for interval in SCREENER_INTERVALS:
        tensor,  helper = json.loads(data.cache.get(f'{interval}_screener')), json.loads(data.cache.get(f'{interval}_screener_helper'))
        cacheDataDict[interval] = tensor, helper
    with data.db.cursor() as cursor:
        for ticker_id, ticker in tqdm(tickers):
            df = yf.download(tickers = ticker, period = '5d', group_by='ticker', interval = '1m', ignore_tz = False, auto_adjust=True, progress=False, show_errors = False, threads = True, prepost = True) 
            df.dropna(inplace = True)
            if df.empty:
                continue
            df = df.reset_index().to_numpy()
            #np.set_printoptions(threshold=np.inf)
            for interval in SCREENER_INTERVALS:
                tensor, helper = cacheDataDict[interval]
                tensor, helper = updateCache(data, df, ticker_id, interval, tensor, helper)
                cacheDataDict[interval] = tensor, helper
            setQuotes(cursor,ticker_id,data,df)
    for interval in SCREENER_INTERVALS:
        tensor, helper = cacheDataDict[interval]
        data.cache.tensor_set(f'{interval}_screener', json.dumps(tensor))
        data.cache.set(f'{interval}_screener_helper', json.dumps(helper))


def updateTickers():
    #TODO
    return

def nightUpdate(data):
    #new tickers?
    updateTickers()
    for interval in SCREENER_INTERVALS:
        data.cache.delete(f'{interval}_screener')
        data.cache.delete(f'{interval}_screener_helper')
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

    for interval in SCREENER_INTERVALS:
        tensor, helper = newCache(data,interval,data.getTickers())
        data.cache.tensor_set(f'{interval}_screener', json.dumps(tensor))
        data.cache.set(f'{interval}_screener_helper', json.dumps(helper))


def update(data, case):
    if case == 1:
        dayUpdate(data)
    elif case == 2:
        nightUpdate(data)
    else:
        raise ValueError('Invalid case')

if __name__ == '__main__':
    update(Data(False), 1)

