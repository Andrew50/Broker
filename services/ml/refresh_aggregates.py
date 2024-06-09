from data import Data
from psycopg2 import sql
import traceback
from tqdm import tqdm
import multiprocessing
import datetime


CPUS = 25
SLICE_SIZE_DAYS = 50
incontainer = False

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

def refresh_all_aggregates(aggregates, base_table, slice_size_days=SLICE_SIZE_DAYS):
    print('fetching date range')
    #start_date, end_date = get_date_range(base_table)
    start_date, end_date = datetime.datetime(2008,1,1), datetime.datetime.now()
    date_slices = get_date_slices(start_date, end_date, slice_size_days)
    print('starting refresh')
    with multiprocessing.Pool(processes=CPUS) as pool:
        list(tqdm(pool.imap_unordered(refresh_aggregates, [[start_date, end_date, aggregates] for start_date, end_date in date_slices]), total=len(date_slices), desc="Refreshing aggregates"))

if __name__ == "__main__":
    aggregates = ['quotes_h_extended', 'quotes_h', 'quotes_d', 'quotes_w']
    base_table = 'quotes_1_extended'
    refresh_all_aggregates(aggregates, base_table)
