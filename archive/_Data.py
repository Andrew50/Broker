
import numpy as np
import  pandas as pd, numpy as np, datetime, mysql.connector, pytz, redis, pickle,  multiprocessing
try:
	from Database import Database
except:
	from .Database import Database
#ben

class Main:
	
	def formatDataframeForMatch(self, onlyCloseAndVol = True, whichColumn=4):
		obj = False
		if isinstance(self,Data):
			obj = True
			df = self.df
		else:
			df = self
		length = len(df)
		
		if onlyCloseAndVol: 
			if(length < 3): return np.zeros((1, 4))
			d = np.zeros((length-1, 4))
			for i in range(1, length):
				close = df[i,whichColumn]
				d[i-1] = [close, (close/df[i-1,whichColumn]) - 1, df[i, 5], df[i, 0]]
			if not obj:
				return d
			self.df = d


	def is_market_open(self=None):
		if (datetime.datetime.now().weekday() >= 5):
			return False
		dt = datetime.datetime.now(pytz.timezone('US/Eastern'))
		hour = dt.hour
		minute = dt.minute
		if hour >= 10 and hour <= 16:
			return True
		elif hour == 9 and minute >= 30:
			return True
		return False


	
	def format_datetime(dt,reverse=False):
		if reverse:
			return datetime.datetime.fromtimestamp(dt)
			
		if type(dt) == int or type(dt) == float:
			return dt
		if dt is None: return None
		if dt == 'current': return datetime.datetime.now(pytz.timezone('EST'))
		if isinstance(dt, str):
			try: dt = datetime.datetime.strptime(dt, '%Y-%m-%d')
			except: dt = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
		time = datetime.time(dt.hour, dt.minute, 0)
		dt = datetime.datetime.combine(dt.date(), time)
		if dt.hour == 0 and dt.minute == 0:
			time = datetime.time(9, 30, 0)
			dt = datetime.datetime.combine(dt.date(), time)
		#return dt
		dt = dt.timestamp()
		return dt

class Dataset:
	
	def __init__(self, db, request='full',tf='1d', bars=0, format = 'normalized'):
		
		if request == 'full':
			
			if db.type == 'sql':
				data = db.get_ds(tf,format)
			elif db.type =='redis':
				data = db.get_hash(tf+format)

		else:
			raise Exception('to be coded')
		#if debug:
		#	request = request[:debug,:,:]

		self.data = data
		

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
			data = db.get_df(tf,ticker,format)
		elif db.type == 'redis':
			data = db.get_hash(tf+format,ticker)
		#print(data)
		if dt:
			index = Data.findex(data,dt)
			data = data[:index+1]
		if bars:
			data = data[:-50]
		#if format == 'normal':
		#	pass
	#	elif format == 'match':
			
		#elif format == 'screener':
	#		raise Exception('godgogogd ging ging')
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