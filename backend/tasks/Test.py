

# df = pd.read_feather(f'C:/Stocks2/local/data/d_{st}.feather')[['ticker','dt','value']]
# df['dt'] = df['dt'].astype(str).apply(data.format_datetime)
# print(len(df[df['value'] == 1]))

# #print(df[df['value'] == 1])


# df = df.values.tolist()

# user_id = 6
# data.set_setup_sample(user_id,st,df)
























# import ftplib
# import os
# ftp = ftplib.FTP("ftp.nasdaqtrader.com")
# ftp.login("anonymous", "")
# ftp.cwd("SymbolDirectory")
# files_to_download = ["nasdaqlisted.txt", "otherlisted.txt"]
# for file in files_to_download:
#   with open(file, "wb") as f:
#     print(f)
#     #ftp.retrbinary(f"RETR {file}", f.write)
# ftp.quit()
# import yfinance as yf


# # for tf in ['1d']:
# # 	args = [[ticker, tf, 'C:/dev/broker/backend/' + tf + '/' + ticker + '.feather'] for ticker in self.get_ticker_list()]
# # 	for ticker, tf, path in tqdm(args,desc='Transfering Dataframes'):
# # 		try:
# # 			df = pd.read_feather(path)
# ticker = "TQQQ"
# ytf = '1d'
# period = '25y'
# import pandas as pd
# ydf = yf.download(tickers = ticker, period = period, group_by='ticker', interval = ytf, ignore_tz = True, progress=False, show_errors = False, threads = True, prepost = True) 
# import yfinance as yf
# import datetime
# args = 'AAPL'
# start = datetime.datetime.now()
# ds = yf.download(args, interval='1m', period='1d', prepost=True, auto_adjust=True, threads=True, keepna=False)
# print(datetime.datetime.now() - start)

#data.init_prev_close_cache()

# import yfinance as yf
# import datetime
# import multiprocessing


# #ydf = yf.download(tickers = ticker, period = period, group_by='ticker', interval = ytf, ignore_tz = True, progress=False, show_errors = False, threads = True, prepost = True

# def fetch_stock_data(tickers):
# 	args = " ".join(tickers)
# 	return yf.download(args, interval = '1d',period = '5d')

# def main():
# 	from sync_Data import data
	
# 	tickers = data.get_ticker_list()[:8000]
# 	batches = []
# 	print(len(tickers))
# 	for i in range(0,len(tickers),1000):
# 		batches.append(tickers[i:i+ 1000])
		
# 	with multiprocessing.Pool(8) as pool:
# 		results = pool.map(fetch_stock_data,batches)
	
# 	#for data in results:
# 	#	print(data)

# if __name__ == "__main__":
# 	start = datetime.datetime.now()
# 	main()

# 	#df = data.get_ticker_list()[:100]
# 	#start = datetime.datetime.now()
# 	#df = yf.download(df, period='max', threads=2)
# 	print(datetime.datetime.now() - start)















# import matplotlib.pyplot as plt
# import pandas as pd



# import requests
# import json

# def fetch_intraday_data(symbol, interval, api_key):
#     """
#     Fetch intraday stock data from Alpha Vantage.
#     :param symbol: Stock symbol, e.g., 'MSFT'.
#     :param interval: Time interval (1min, 5min, 15min, 30min, 60min).
#     :param api_key: Your Alpha Vantage API key.
#     :return: JSON data containing intraday stock prices.
#     """
#     url = f'https://www.alphavantage.co/query?function=TIME_SERIES_INTRADAY&symbol={symbol}&interval={interval}&apikey={api_key}'

#     response = requests.get(url)
#     if response.status_code == 200:
#         return response.json()
#     else:
#         return None

# # Replace 'YOUR_API_KEY' with your actual Alpha Vantage API key
# api_key = 'SWRPM3EKAI88TYU2'

# # Example usage
# symbol = 'AAPL'  # Apple Inc
# interval = '1min'  # 5 minutes interval
# data = fetch_intraday_data(symbol, interval, api_key)

# if data:
#     print(json.dumps(data, indent=4))
# else:
#     print("Failed to retrieve data")
	

# df = pd.DataFrame(data).T
# df.index = pd.to_datetime(df.index)
# df = df.astype(float)

# # Plotting
# plt.figure(figsize=(10, 6))
# plt.plot(df.index, df['4. close'], label='Close Price', color='blue')
# plt.plot(df.index, df['1. open'], label='Open Price', color='green')
# plt.fill_between(df.index, df['2. high'], df['3. low'], color='gray', alpha=0.3)
# plt.title('Stock Price Data')
# plt.xlabel('Time')
# plt.ylabel('Price')
# plt.legend()
# plt.grid(True)
# plt.xticks(rotation=45)
# plt.tight_layout()
# plt.show()


# start = datetime.datetime.now()
# ticker = "AAPL"
# tf = '1min'
# if tf == '1d':
						
# 	ytf = '1d'
# 	period = '25y'
# elif tf == '1min':
# 	ytf = '1m'
# 	period = '5d'
# else:
# 	raise Exception('invalid timeframe to update')
# ydf = yf.download(tickers = ticker, period = period, group_by='ticker', interval = ytf, ignore_tz = True, progress=False, show_errors = False, threads = True, prepost = True) 
# ydf.drop(axis=1, labels="Adj Close",inplace = True)
# ydf.dropna(inplace = True)

# ydf = yf.download(tickers = ticker, period = period, group_by='ticker', interval = ytf, ignore_tz = True, progress=False, show_errors = False, threads = True, prepost = True) 

# print(datetime.datetime.now() - start)






# nasdaq_tickers = yf.Tickers('NASDAQ').tickers
# nyse_tickers = yf.Tickers('NYSE').tickers
# amex_tickers = yf.Tickers('AMEX').tickers
# print(amex_tickers,nasdaq_tickers,nyse_tickers)
#full_ticker_list = nasdaq_tickers + nyse_tickers + amex_tickers
#print(full_ticker_list)
	
#print(data.get_df('screener','HWBK','1d'))



