
import numpy as np
import os, time
import pandas as pd
import datetime
import pytz
from Data import Main as main
from multiprocessing import Pool
path1 = 'C:/Stocks/local/data/d/'
path2 = 'C:/Stocks2/local/data/d/'
import os

df = Data()
plot = df.load_plot()
# if __name__ == '__main__':
#     main.train('d_EP',200,.05)

# def pool(deff,arg):
# 	pool = Pool()
# 	data = list(tqdm(pool.imap_unordered(deff, arg), total=len(arg)))
# 	return data

# def format_date(dt):
# 		if dt == 'current': return datetime.datetime.now(pytz.timezone('EST'))
# 		if dt == None: return None
# 		if isinstance(dt,str):
# 			try: dt = datetime.datetime.strptime(dt, '%Y-%m-%d')
# 			except: dt = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
# 		time = datetime.time(dt.hour,dt.minute,0)
# 		dt = datetime.datetime.combine(dt.date(),time)
# 		if dt.hour == 0 and dt.minute == 0:
# 			time = datetime.time(9,30,0)
# 			dt = datetime.datetime.combine(dt.date(),time)
# 		return dt
# def findex(df,dt):
# 	dt = format_date(dt)
# 	i = int(len(df)/2)
# 	k = int(i/2)
# 	while k != 0:
# 		date = df.index[i].to_pydatetime()
# 		if date > dt: i -= k
# 		elif date < dt: i += k
# 		k = int(k/2)
# 	while df.index[i].to_pydatetime() < dt: i += 1
# 	while df.index[i].to_pydatetime() > dt: i -= 1
# 	return i



# def main (bar):
# 	try:
# 		path, reference_df = bar
# 		df = pd.read_feather(path1 + path)
# 		print(df)
# 		dt = df.iat[0,0]
# 		index = findex(reference_df,dt)
# 		df = df.to_numpy()
	
# 		df[:,0] = np.arange(index,len(df)+ index )
# 		print(df)
	
	
	

# 		np.save(path2 + path[:-7] + 'npy', df)
# 	except:
# 		pass
	

# if __name__ == '__main__':
# 	items = os.listdir(path1)
	
# 	reference_df = pd.read_feather('C:/Stocks/local/data/d/AAPL.feather').set_index('datetime')
# 	arglist = [[path,reference_df] for path in items]
# 	pool(main,arglist)
	







