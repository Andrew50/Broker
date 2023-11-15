from re import T
from tasks.Data import Database, Cache, Data
import uvicorn, traceback, multiprocessing, tqdm, datetime

def startup_worker(ticker):
    
    df = Database().get_df(ticker)
    df = Data.formatDataframeForMatch(df)
    
    return [df,ticker]           
    
if __name__ == '__main__':
    try:
        start = datetime.datetime.now()
        cache = Cache()
        db = Database()
        ticker_list = db.get_ticker_list()
        ds = []
        pool = multiprocessing.Pool()
        for df in pool.imap_unordered(startup_worker, ticker_list):
            ds.append(df)
        pool.close()
        pool.join()
        #ds = multiprocessing.Pool().imap_unordered(startup_worker,ticker_list)
        cache.set_hash(ds,'ds')
        print(datetime.datetime.now() - start,flush = True)
            
    except Exception as e:
        print(traceback.format_exc() + str(e),flush=True)


    uvicorn.run("api:app", host="0.0.0.0", port=5057, reload=True)