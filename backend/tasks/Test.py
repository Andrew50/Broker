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

from Database import Cache

print(Cache().get_hash('1dnormalized'))