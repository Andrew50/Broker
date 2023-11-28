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
# print(ydf)
from sync_Data import data
data.update()
#from Data import data
#from Data import Data

# df = pd.read_feather('C:/Stocks2/local/data/d_EP.feather')[['ticker','dt','value']]
# #df['dt'] = df['dt'].astype(str).apply(Data.format_datetime)

# print(len(df[df['value'] == 1]))
# print(df[df['value'] == 1])


#df = df.values.tolist()

#data.set_setup_sample(4,'EP',df)


