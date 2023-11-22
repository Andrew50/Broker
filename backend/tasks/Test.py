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




# for tf in ['1d']:
# 	args = [[ticker, tf, 'C:/dev/broker/backend/' + tf + '/' + ticker + '.feather'] for ticker in self.get_ticker_list()]
# 	for ticker, tf, path in tqdm(args,desc='Transfering Dataframes'):
# 		try:
# 			df = pd.read_feather(path)

import pandas as pd

from Data import data
from Data import Data

df = pd.read_feather('C:/Stocks/local/data/d_EP.feather')[['ticker','dt','value']]
df['dt'] = df['dt'].astype(str).apply(Data.format_datetime)





df = df.values.tolist()

data.set_setup_sample(4,'EP',df)


