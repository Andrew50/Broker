from tqdm import tqdm
import traceback
from multiprocessing import Pool
from data import Data
import numpy as np, yfinance as yf, json, datetime 
from data import Data
from psycopg2 import sql
import traceback
import multiprocessing
import datetime
SCREENER_INTERVALS = "1d",
CPUS = 15
SLICE_SIZE_DAYS = 50
incontainer = False

market_open = datetime.time(9, 30, 0)
market_close = datetime.time(16, 0, 0)



def get_date_slices(start_date, end_date, slice_size_days):
    slices = []
    current_start = start_date
    while current_start < end_date:
        current_end = min(current_start + datetime.timedelta(days=slice_size_days), end_date)
        slices.append((current_start, current_end))
        current_start = current_end
    return slices

def get_date_range(base_table):
    conn = Data(incontainer).db
    cur = conn.cursor()
    cur.execute(f"SELECT MIN(t), MAX(t) FROM {base_table};")
    start_date, end_date = cur.fetchone()
    cur.close()
    conn.close()
    return start_date, end_date

def refresh_aggregates(bar):
    try:
        start_date, end_date, aggregates = bar
        conn = Data(incontainer).db
        conn.autocommit = True
        cur = conn.cursor()
        for aggregate in aggregates:
#        query = sql.SQL("CALL refresh_continuous_aggregate({}, %s, %s);").format(sql.Identifier(aggregate))
            query = sql.SQL(f"CALL refresh_continuous_aggregate('{aggregate}', %s, %s);")
            cur.execute(query, (start_date, end_date))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(traceback.print_exception)

def refresh_all_aggregates(aggregates, t, slice_size_days=SLICE_SIZE_DAYS):
    end_date = datetime.datetime.now()
    if t is None:
        start_date = datetime.datetime(2008,1,1)
    else:
        start_date = t
    date_slices = get_date_slices(start_date, end_date, slice_size_days)
    with multiprocessing.Pool(processes=CPUS) as pool:
        list(tqdm(pool.imap_unordered(refresh_aggregates, [[start_date, end_date, aggregates] for start_date, end_date in date_slices]), total=len(date_slices), desc="Refreshing aggregates"))


def refreshAggregates(t):
    aggregates = ['quotes_h_extended', 'quotes_h', 'quotes_d', 'quotes_w']
    base_table = 'quotes_1_extended'
    refresh_all_aggregates(aggregates, t)


def cacheTensor(data, key: str, tensor):
    tensorJson = json.dumps(tensor.tolist())
    data.cache.set(key, tensorJson)

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
        for ticker_id, ticker in tqdm(tickers,disable=False):
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
            mcap = 100000000000 #TODO 10 billion
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

def setQuotes(ticker_id,data,df):
    with data.db.cursor() as cursor:
        if data.is_market_open(pm = True):
            df = df[:-1]
        cursor.execute('SELECT MAX(t) FROM quotes_1_extended WHERE ticker_id = %s;', (ticker_id,))
        last_timestamp = cursor.fetchone()[0]
        if last_timestamp is not None:
            #last_timestamp = int(last_timestamp)
            try:
                index = data.findex(df, last_timestamp) 
                df = df[index + 1:,:]
            except:
                print("findex error, still updating")
        df = [(ticker_id, row[0].time() >= market_open and row[0].time() < market_close,
        row[0], row[1], row[2], row[3], row[4], row[5]
        ) for row in df.tolist()]
        insert_query = """
        INSERT INTO quotes_1_extended (ticker_id, extended_hours, t, open, high, low, close, volume) 
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        """
        cursor.executemany(insert_query, df)
    data.db.commit()

def loop (bar):
    tickers, ticker_ids = bar["tickers"], bar["ticker_ids"]
    failed = []
    data = Data()
    query = " ".join(tickers)
    #print(query)
    download = yf.download(tickers = query, period = '5d', group_by='ticker', interval = '1m', ignore_tz = False, auto_adjust=True, progress=True, show_errors = True, threads = True, prepost = True) 
    input()
    #return
    print('worked')
    ds = download.to_numpy()
    print(ds.shape)
    print(ds)
    for i in range(download.shape[0]):
        df = ds[i,:,:]
        try:
            df.dropna(inplace = True)
            if df.empty:
                print(f"{ticker} was empy")
                continue
            df = df.reset_index().to_numpy()
            setQuotes(cursor,ticker_id,data,df)
        except TimeoutError as e:
            traceback.print_exc()
            print(e)
            print(ticker_id,ticker,"failed")
    return failed

def dayUpdate(data):
    """
    single interval (1d) updating. if cache nonexistent then will calc new cache
    """
    tickers = data.getTickers()
    batch_size = 200
    batches = len(tickers) // batch_size + 1
    args = [{"tickers":[], 
            "ticker_ids":[]} for _ in range(batches)]
    i = 0
    for  ticker_id, ticker in tickers:
        args[i%batches]["tickers"].append(ticker)
        args[i%batches]["ticker_ids"].append(ticker_id)
        i += 1
    with Pool(CPUS) as p:
        failed = p.map(loop,args)
    print(len(failed))
    failed = loop(tickers)
    loop(failed)
    last_refresh  = pickle.loads(data.cache.get("last_refresh"))
    refreshAggregates(last_refresh)
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

def update(data, case=1):
    if case == 1:
        dayUpdate(data)
    elif case == 2:
        nightUpdate(data)
    else:
        raise ValueError('Invalid case')

if __name__ == '__main__':
    update(Data(False), 1)

