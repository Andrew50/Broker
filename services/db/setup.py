#transfer2.py
from io import StringIO
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
from tqdm import tqdm  # Import tqdm for the progress bar
import psycopg2

market_open = datetime.time(9, 30, 0)
market_close = datetime.time(16, 0, 0)
dir = "/home/aj/dev/broker/services/db/feather/"
def connect():
    db_host = 'localhost'
    return psycopg2.connect(host=db_host,port='5432',user='postgres',password='pass')

def process_file(filename):
    try:
        ticker = filename.split(".")[0]
        with connect().cursor() as cursor:
            cursor.execute("SELECT ticker_id FROM tickers WHERE ticker = %s", (ticker,))
            result = cursor.fetchone()
            if result is None:
                return f"Ticker not found: {ticker}"
            ticker_id = result[0]
            df = pd.read_feather(os.path.join(dir, filename))
            df['extended_hours'] = df['datetime'].dt.time.between(market_open, market_close)
            df['ticker_id'] = ticker_id
            df = df[['ticker_id', 'extended_hours', 'datetime', 'open', 'high', 'low', 'close', 'volume']]
            df.to_csv(f"/home/aj/dev/broker/services/db/csv/{ticker}.csv", index=False, header=False)
    except Exception as e:
        return f"Error processing {filename}: {e}"


files = [f for f in os.listdir(dir) if f.endswith(".feather")]
ticker_list = pd.read_csv("/home/aj/dev/broker/services/db/listed_tickers.csv")
ticker_list['listed'] = True  
tickers_from_files = [f.replace('.feather', '') for f in files]  # Remove the .feather extension
unlisted = pd.DataFrame(tickers_from_files, columns=['ticker'])
unlisted['listed'] = False  
combined_ticker_list = pd.concat([ticker_list, unlisted])
combined_ticker_list = combined_ticker_list.drop_duplicates(subset='ticker', keep='first')
combined_ticker_list.to_csv("/home/aj/dev/broker/services/db/tickers.csv", index=False)

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(process_file, file): file for file in files}
    for future in tqdm(as_completed(futures), total=len(futures), desc="Processing Files"):
        if future.result() is not None:
            print(future.result())
