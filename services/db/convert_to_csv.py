#transfer2.py
from io import StringIO
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
from tqdm import tqdm  # Import tqdm for the progress bar

market_open = datetime.time(9, 30, 0)
market_close = datetime.time(16, 0, 0)
dir = "/home/aj/dev/broker/services/db/feather/"
def process_file(arg):
    ticker_id, ticker, listed = arg
    if os.path.isfile(f"/home/aj/dev/broker/services/db/quotes/{ticker}.csv"):
        return f"{ticker} already done"
    if isinstance(ticker,float) or "." in ticker or "/" in ticker:
        return f"skipped {ticker}"
    try:
        df = pd.read_feather(os.path.join(dir, ticker + ".feather"))
#        df['datetime'] = df['datetime'].dt.tz_localize('US/Eastern').dt.tz_convert('US/Eastern').dt.tz_localize(None)
        df['extended_hours'] = ~df['datetime'].dt.time.between(market_open, market_close)
        df['ticker_id'] = ticker_id
        df = df[['ticker_id', 'extended_hours', 'datetime', 'open', 'high', 'low', 'close', 'volume']]
        df.to_csv(f"/home/aj/dev/broker/services/db/quotes/{ticker}.csv", index=False, header=False)
    except Exception as e:
        return f"Error processing {ticker}: {e}"


files = [f for f in os.listdir(dir) if f.endswith(".feather")]
ticker_list = pd.read_csv("/home/aj/dev/broker/services/db/data/old_ticker_list.csv")
ticker_list['listed'] = True  
tickers_from_files = [f.replace('.feather', '') for f in files]  # Remove the .feather extension
unlisted = pd.DataFrame(tickers_from_files, columns=['ticker'])
unlisted['listed'] = False  
combined_ticker_list = pd.concat([ticker_list, unlisted])
combined_ticker_list = combined_ticker_list.drop_duplicates(subset='ticker', keep='first')
combined_ticker_list = combined_ticker_list[pd.notna(combined_ticker_list['ticker']) & combined_ticker_list['ticker'].str.strip().astype(bool)]
combined_ticker_list.reset_index(inplace=True)
combined_ticker_list["ticker_id"] = combined_ticker_list.index + 1
combined_ticker_list = combined_ticker_list[["ticker_id", "ticker", "listed"]]
combined_ticker_list.to_csv("/home/aj/dev/broker/services/db/data/tickers.csv", index=False)
args = combined_ticker_list.values.tolist()

with ThreadPoolExecutor(max_workers=10) as executor:
    futures = {executor.submit(process_file, arg): arg for arg in args}
    for future in tqdm(as_completed(futures), total=len(futures), desc="Processing Files"):
        if future.result() is not None:
            print(future.result())
