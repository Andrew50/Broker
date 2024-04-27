from tqdm import tqdm
from data import Data
import time, numpy as np, yfinance as yf, json, datetime
SCREENER_INTERVALS = "1d",

market_open = datetime.time(9, 30, 0)
market_close = datetime.time(16, 0, 0)

def updateCache(data, df, ticker, screenerTensor, screenerKey):

    log_1, log_0, next_update = helper[ticker]
    if time.now() >= next_update:
        new = log



    """
    else: #update cache
        if ticker_id in screenerKey:
            index = screenerKey.index(ticker_id)
            base = screenerTensor[index,:,:]


    #push to tensor in redis AI at 1d_screener
    #push key to 1d_screener_key
    """

def setCache(data,interval,tickers):
    if interval != "1d":
        raise Exception("good luck")
    table, bucket, aggregate = data.getQueryInfo(interval, pm)
    bars = 100
    queries = []
    for ticker_id, ticker in tickers:
        if aggregate:
            raise Exception("Aggregation not implemented for models...yet?")
            query = f"""
                (SELECT
                    bucket,
                    LOG(first_open) - LAG(LOG(last_close), 1) OVER (ORDER BY bucket) AS log_diff_open,
                    LOG(max_high) - LAG(LOG(last_close), 1) OVER (ORDER BY bucket) AS log_diff_high,
                    LOG(min_low) - LAG(LOG(last_close), 1) OVER (ORDER BY bucket) AS log_diff_low,
                    LOG(last_close) - LAG(LOG(last_close), 1) OVER (ORDER BY bucket) AS log_diff_close
                FROM (
                    SELECT
                        time_bucket('{bucket}', q.t) AS bucket,
                        first(q.open, q.t) AS first_open,
                        max(q.high) AS max_high,
                        min(q.low) AS min_low,
                        last(q.close, q.t) AS last_close
                    FROM {table} AS q
                    WHERE q.ticker_id = {ticker_id}
                    GROUP BY bucket
                    ORDER BY bucket DESC
                    LIMIT {bars}
                ) AS subquery
                ORDER BY bucket ASC)
                """
        else:
           query = f"""
                (SELECT
                    bucket,
                    LOG(first_open) - LAG(LOG(last_close), 1) OVER (ORDER BY bucket) AS log_diff_open,
                    LOG(max_high) - LAG(LOG(last_close), 1) OVER (ORDER BY bucket) AS log_diff_high,
                    LOG(min_low) - LAG(LOG(last_close), 1) OVER (ORDER BY bucket) AS log_diff_low,
                    LOG(last_close) - LAG(LOG(last_close), 1) OVER (ORDER BY bucket) AS log_diff_close
                FROM (
                    SELECT
                        q.t AS bucket,
                        q.open AS first_open,
                        q.high AS max_high,
                        q.low AS min_low,
                        q.close AS last_close
                    FROM {table} AS q
                    WHERE q.ticker_id = {ticker_id}
                    ORDER BY q.t DESC
                    LIMIT {bars}
                ) AS subquery
                ORDER BY bucket ASC)
                """
        queries.append(query)
    combined_query = " UNION ALL ".join(queries)
    with data.db.cursor() as cursor:
        cursor.execute(combined_query)
        results = cursor.fetchall()
    ds = []
    keys = []
    for result, i in enumerate(results):
        if len(result) != bars:
            #pad
            continue
        #result = [np.inf for _ in range(4)] + result
        keys.append(tickers[i][0])
        ds.append(results)
    ds = np.array(ds)
    classes = np.array(classes)
    return ds, classes

def setData(cursor,ticker_id,data,df):
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

def update1(data):
    tickers = data.getTickers()
    cacheDataDict = {}
    for interval in SCREENER_INTERVALS:
        tensor, key, helper = data.cache.get(f'{interval}_screener'), data.cache.get(f'{interval}_screener_key'), data.cache.get(f'{interval}_screener_helper')
        _update = tensor is not None and key is not None and helper is not None

        cacheDataDict[interval] = tensor, key, helper, _update
    with data.db.cursor() as cursor:
        for ticker_id, ticker in tqdm(tickers):
            df = yf.download(tickers = ticker, period = '5d', group_by='ticker', interval = '1m', ignore_tz = False, auto_adjust=True, progress=False, show_errors = False, threads = True, prepost = True) 
            df.dropna(inplace = True)
            if df.empty:
                continue
            df = df.reset_index().to_numpy()
            #np.set_printoptions(threshold=np.inf)
            
            for interval in SCREENER_INTERVALS:
                tensor, key, helper, _update = cacheDataDict[interval]
                if _update:
                    tensor, key, helper = updateCache(data, df, ticker, tensor, key, helper)
                    cacheDataDict[interval] = tensor, key, helper, _update
            setData(cursor,ticker_id,data,df)
    for interval in SCREENER_INTERVALS:
        tensor, key, helper, _update = cacheDataDict[interval]
        if not _update:
            tensor, key, helper = getCache(data,interval,tickers)
        data.cache.tensor_set(f'{interval}_screener', tensor)
        data.cache.set(f'{interval}_screener_key', json.dumps(key))
        data.cache.set(f'{interval}_screener_helper', json.dumps(helper))

def update2(data):
    #new tickers?
#clear temp (cahce, any key thats just a uuid) -- dont because just delete after each 
    data.cache.delete('temp')
    data.cache.delete('task_queue_1')
    data.cache.delete('task_queue_2')
    for interval in SCREENER_INTERVALS:
        data.cache.delete(f'{interval}_screener')
        data.cache.delete(f'{interval}_screener_key')
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


def update(data, case):
    if case == 1:
        update1(data)
    elif case == 2:
        update2(data)
    else:
        raise ValueError('Invalid case')

if __name__ == '__main__':
    update(Data(False), 1)

