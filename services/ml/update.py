from tqdm import tqdm
import io, base64
from data import Data
import time, numpy as np, yfinance as yf, json, datetime, math
SCREENER_INTERVALS = "1d",

market_open = datetime.time(9, 30, 0)
market_close = datetime.time(16, 0, 0)

def updateCache(data, df, ticker_id, interval, screenerTensor, helper):

    log_1 = helper[ticker_id]
    key = screenerTensor[:,0,4]
    if ticker_id in key:
        index = screenerTensor.index(ticker_id)
    else:
        raise Exception('man')
    screenerTensor[index,-1,:] = np.array([math.log(x) - log_1 for x in df[-1]])
    return screenerTensor, helper


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


def cacheArray(data, key: str, array):
    buffer = io.BytesIO()
    np.save(buffer,array)
    arrayBin = buffer.getvalue()
    array_base64 = base64.b64encode(arrayBin).decode('utf-8')
    data.cache.set(key,array_base64)

def newCache(data):
    tickers = data.getTickers()
    for interval in SCREENER_INTERVALS:
        bars = 100
        l = 20
        pm = False
        table, bucket, aggregate = data.getQueryInfo(interval, pm)
        ds = []
        key = []
        zeroArrays = 0
        for ticker_id, ticker in tqdm(tickers):
            query = ""
            if aggregate:
                raise Exception('to code')
            else:
                query = f"""SELECT open, high, low, close, volume
                            FROM {table}
                            WHERE ticker_id = {ticker_id}
                            ORDER BY t DESC
                            LIMIT {bars + 1}"""
            with data.db.cursor() as cursor:
                cursor.execute(query)
                df = cursor.fetchall()
            if len(df) == 0:
                #print(f"zero l#en array hit on {ticker}")
                zeroArrays += 1
                continue
            df = np.array(df, dtype=np.float64)
            dolvol = np.mean(df[-l:,4]) * np.mean(df[-l:,3])
            adr = (np.mean((df[-l:,1] / df[-l:,2])) - 1 ) * 100
            mcap = np.inf #TODO
            df = df[:,:4]
            df = np.log(df)
            close = df[:-1,3]
            df = df[1:,:] - close[:,np.newaxis]
            metadata = np.array([[dolvol,adr,mcap,ticker_id]])
            if len(df) < bars:
                df = np.concatenate([df,np.zeros((bars - len(df),4))], axis=0)
            df = np.concatenate([metadata,df], axis = 0)
            ds.append(df)
        print(f'{zeroArrays} empty arrays')
        tensor = np.stack(ds)
        helper = np.array(key)
        cacheArray(data,f'{interval}_screener',tensor)
        cacheArray(data,f'{interval}_screener_helper',helper)

def setQuotes(cursor,ticker_id,data,df):
    if data.is_market_open(pm = True):
        df = df[:-1]
    #cursor.execute('SELECT EXTRACT(EPOCH FROM MAX(t)) FROM quotes_1_extended WHERE ticker_id = %s;', (ticker_id,))

    cursor.execute('SELECT MAX(t) FROM quotes_1_extended WHERE ticker_id = %s;', (ticker_id,))
    last_timestamp = cursor.fetchone()[0]
    if last_timestamp is not None:
        #last_timestamp = int(last_timestamp)
        try:
            index = data.findex(df, last_timestamp) 
            df = df[index + 1:,:]
        except TimeoutError:
            print("findex error")
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
    """
    single interval (1d) updating. if cache nonexistent then will calc new cache
    """
    interval = "1d"
    tickers = data.getTickers()
#    tensorJson, helperJson = data.cache.get(f'{interval}_screener'), data.cache.get(f'{interval}_screener_helper')
    #if tensorJson is None or helperJson is None:
#    cacheExists = False
    #else:
#        tensor_binary = base64.b64decode(tensorJson)
#        helper_binary = base64.b64decode(helperJson)
#        tensor = np.load(io.BytesIO(tensor_binary))
#        helper = np.load(io.BytesIO(helper_binary))
#        print(tensor.shape)
#        print(helper.shape)
#        cacheExists = True
#    #hard code
#    cacheExists = False
    with data.db.cursor() as cursor:
        for ticker_id, ticker in tqdm(tickers):
            try:
                df = yf.download(tickers = ticker, period = '5d', group_by='ticker', interval = '1m', ignore_tz = False, auto_adjust=True, progress=False, show_errors = False, threads = True, prepost = True) 
                df.dropna(inplace = True)
                if df.empty:
                    continue
                df = df.reset_index().to_numpy()
    #            if cacheExists:
    #                tensor, helper = updateCache(data,df, ticker_id, interval, tensor, helper)
                setQuotes(cursor,ticker_id,data,df)
            except Exception as e:
                raise(e)
                print(e)
    #if cacheExists:
        #cacheArray(data,f'{interval}_screener',tensor)
        #cacheArray(data,f'{interval}_screener_helper',helper)
    #else:
    newCache(data)
    

#def dayUpdate(data):
#    tickers = data.getTickers()
#    cacheDataDict = {}
#    for interval in SCREENER_INTERVALS:
#        tensorJson, helperJson = data.cache.get(f'{interval}_screener'), data.cache.get(f'{interval}_screener_helper')
#        if tensorJson is None or helperJson is None:
#            emptyCache = True
#        else:
#            emptyCache = False
#            cacheDataDict[interval] = json.loads(tensorJson), json.loads(helperJson)
#    with data.db.cursor() as cursor:
#        for ticker_id, ticker, listed in tqdm(tickers):
#            df = yf.download(tickers = ticker, period = '5d', group_by='ticker', interval = '1m', ignore_tz = False, auto_adjust=True, progress=False, show_errors = False, threads = True, prepost = True) 
#            df.dropna(inplace = True)
#            if df.empty:
#                continue
#            df = df.reset_index().to_numpy()
#            for interval in SCREENER_INTERVALS:
#                tensor, helper = cacheDataDict[interval]
#                cacheDataDict[interval]  = updateCache(data, df, ticker_id, interval, tensor, helper)
#            setQuotes(cursor,ticker_id,data,df)
#    for interval in SCREENER_INTERVALS:
#        tensor, helper = cacheDataDict[interval]
#        data.cache.tensor_set(f'{interval}_screener', json.dumps(tensor))
#        data.cache.set(f'{interval}_screener_helper', json.dumps(helper))


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

def update(data, case):
    if case == 1:
        dayUpdate(data)
    elif case == 2:
        nightUpdate(data)
    else:
        raise ValueError('Invalid case')

if __name__ == '__main__':
    update(Data(False), 1)

