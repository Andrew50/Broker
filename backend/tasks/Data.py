
import numpy as np
import  pandas as pd, numpy as np, datetime, mysql.connector, pytz, redis, pickle,  multiprocessing
from tqdm import tqdm
from collections import defaultdict
import yfinance as yf
from Database import Database, Cache
#ben

class Dataset:
	
	def __init__(self, db, request='full',tf='1d', bars=0, debug = 0, format = 'normalized'):
		
		if request == 'full' and format == 'normalized':
			
			if db.type == 'sql':
				data = db.get_ds(tf)
			elif db.type =='redis':
				data = db.get_hash(tf)

		else:
			raise Exception('to be coded')
		if debug:
			request = request[:debug,:,:]
		if db.type == 'sql':
			Data
	
		self.dfs = []
		i = 0
		for ticker,dt in request:
			self.dfs.append(Data(db,ticker, tf, dt, bars, value, pm))
			i += 1
		self.bars = bars
		

	def formatDataframesForMatch(self):
		for df in self:
			df.formatDataframeForMatch()
			
	

class Data:
	
	def findex(df, dt):
		dt = Database.format_datetime(dt)
		i = int(len(df)/2)		
		k = int(i/2)
		while k != 0:
			date = df.index[i]
			if date > dt:
				i -= k
			elif date < dt:
				i += k
			k = int(k/2)
		while df.index[i] < dt:
			i += 1
		while df.index[i] > dt:
			i -= 1
		return i

	def __init__(self, db, ticker='QQQ', tf='1d', dt=None, bars=0,value=None, pm=True, format = 'normal'):
		if db.type == 'sql':
			data = db.get_df(tf,ticker)
		elif db.type == 'redis':
			data = db.get_hash(tf,ticker)
		print(data)
		if dt:
			index = Data.findex(data,dt)
			data = data[:index+1]
		if bars:
			data = data[:-50]
		if format == 'normal':
			pass
		elif format == 'match':
			length = len(data)
			d = np.zeros((length-1, 4))
			for i in range(1, length):
				close = data[i,4]
				d[i-1] = [close, (close/data[i-1,4]) - 1, data[i, 5], data[i, 0]]
		elif format == 'screener':
			raise Exception('godgogogd ging ging')
		self.data = data
			
		self.len = len(self.data)
		self.ticker = ticker
		self.tf = tf
		self.dt = dt
		self.value = value
		
if __name__ == '__main__':
	db = Database()
	df = Data(db,'AAPL')
	print(df.data)