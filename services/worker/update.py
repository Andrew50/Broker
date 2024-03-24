import pandas as pd, numpy as np, yfinance as yf, pickle

STORED_TFS = '1d',
CACHED_TFS = '1d',
CACHED_FORMATS = 'screener', 'chart'
SCREENER_BARS = 100

def run(data):
    tickers = data.get_tickers('current')
    data.check_connection()
    for ticker in tickers:
        for tf in [*set(STORED_TFS + CACHED_TFS)]:
            try:
                df = data.get_df('raw',ticker,tf)
            except TimeoutError:
                df = np.array([])
            if tf in STORED_TFS:
                df = data.set_df(ticker,tf,df)
            if not df.shape[0]:
                continue
            if tf == '1d':
                dolvol, adr, mcap = data.get_reqs(df[:,1:6])
                data.set_ticker(ticker,dolvol,adr,mcap)
            if tf in CACHED_TFS:
                for format in CACHED_FORMATS:
                    bars = SCREENER_BARS if format == 'screener' else None
                    cdf = data.get_df(format,df = df.copy(),bars = bars)
                    data.set_cache(format, ticker, tf, cdf)
                    #data.cache.hset(tf+'_'+format,ticker,pickle.dumps(data.get_df(format,df =df)))


if __name__ == '__main__':
    from data import Data
    run(Data(False))
