
from data import Data
from io import StringIO
import os
import pandas as pd
from concurrent.futures import ThreadPoolExecutor, as_completed
import datetime
from tqdm import tqdm  # Import tqdm for the progress bar

market_open = datetime.time(9, 30, 0)
market_close = datetime.time(16, 0, 0)
dir = "C:/Stocks/local/data/1min/"

def process_file(filename):
    try:
        data = Data(False)
        if filename.endswith(".feather"):
            ticker = filename.split(".")[0]
            with data.db.cursor() as cursor:
                cursor.execute("SELECT ticker_id FROM tickers WHERE ticker = %s", (ticker,))
                result = cursor.fetchone()
                if result is None:
                    return f"Ticker not found: {ticker}"
                ticker_id = result[0]
                df = pd.read_feather(os.path.join(dir, filename))
                df['extended_hours'] = df['datetime'].dt.time.between(market_open, market_close)
                df['ticker_id'] = ticker_id
                df = df[['ticker_id', 'extended_hours', 'datetime', 'open', 'high', 'low', 'close', 'volume']]
                output = StringIO()
                df.to_csv(output, sep='\t', header=False, index=False)
                output.seek(0)  # Rewind to beginning of the file before reading

# Copy data into the database
                cursor.copy_from(output, 'quotes_1_extended', null="", columns=('ticker_id', 'extended_hours', 't', 'open', 'high', 'low', 'close', 'volume'))
                data.db.commit()
            return f"Processed {filename}"
        else:
            return f"Skipped: {filename}"
    except Exception as e:
        return f"Error processing {filename}: {e}"

# List of files to proce
files = [f for f in os.listdir(dir) if f.endswith(".feather")]

# Using ThreadPoolExecutor to handle files in parallel
with ThreadPoolExecutor(max_workers=10) as executor:
    # Set up tqdm to show the progress bar
    futures = {executor.submit(process_file, file): file for file in files}
    for future in tqdm(as_completed(futures), total=len(futures), desc="Processing Files"):
        print(future.result())  # Optionally print the result from the futures


#                tuples = [tuple(x) for x in df.to_numpy()]
#
#                insert_query = """
#                INSERT INTO quotes_1_extended (ticker_id, extended_hours, t, open, high, low, close, volume) 
#                VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
#                cursor.executemany(insert_query, tuples)
#                """
