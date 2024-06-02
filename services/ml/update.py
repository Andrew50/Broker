from tqdm import tqdm
import io, base64
from data import Data
import time, numpy as np, yfinance as yf, json, datetime, math
SCREENER_INTERVALS = "1d",

market_open = datetime.time(9, 30, 0)
market_close = datetime.time(16, 0, 0)

def cacheTensor(data, key: str, tensor):
    data.cache.set(key, json.dumps(tensor.to_list()))

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
        cacheTensor(data,f'{interval}_screener',tensor)
        #cacheTensor(data,f'{interval}_screener_helper',helper) TODO make this pickled

def setQuotes(cursor,ticker_id,data,df):
    if data.is_market_open(pm = True):
        df = df[:-1]
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
    with data.db.cursor() as cursor:
        for ticker_id, ticker in tqdm(tickers):
            try:
                df = yf.download(tickers = ticker, period = '5d', group_by='ticker', interval = '1m', ignore_tz = False, auto_adjust=True, progress=False, show_errors = False, threads = True, prepost = True) 
                df.dropna(inplace = True)
                if df.empty:
                    continue
                df = df.reset_index().to_numpy()
                setQuotes(cursor,ticker_id,data,df)
            except Exception as e:
                raise(e)
    newCache(data)
    
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

