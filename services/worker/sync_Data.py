import os, numpy as np, time,datetime, mysql.connector, pytz, redis, pickle,  multiprocessing, json, yfinance as yf

class Data:
	
	def __init__(self):

		if os.environ.get('INSIDE_CONTAINER', False): #inside container
			redis_host = 'redis'
			mysql_host = 'mysql'
		else:
			redis_host = 'localhost'
			mysql_host = 'localhost'
		self.redis_conn = redis.Redis(host=redis_host, port=6379)
		self.mysql_conn = mysql.connector.connect(host=mysql_host,port='3306',user='root',password='7+WCy76_2$%g',database='broker')

	def check_connection(self):
		try:
			self.redis_conn.ping()
			self.mysql_conn.ping()
		except:
			self.__init__()

	def get_trainer_queue_size(self,user_id,st):
		return self.redis_conn.llen(str(user_id)+st)

	def set_trainer_queue(self, user_id,st, instance):
		# Add the item to the Redis list
		self.redis_conn.lpush(str(user_id)+st, json.dumps(instance))

	def get_df(self, form='chart', ticker='QQQ', tf='1d', dt=None, bars=0, pm=True):
		#async with self.redis_connedis_pool.get() as conn:
		if form == 'raw':
			with self.mysql_conn.cursor(buffered=True) as cursor:
				cursor.execute("SELECT dt, open, high, low, close, volume FROM dfs WHERE ticker = %s and tf = %s", (ticker,tf))
				data = np.array(cursor.fetchall())
				if dt:
					index = Data.findex(data,dt)
					data = data[:index+1]
					return data
		data = self.redis_conn.hget(tf+form,ticker)
		if not form == 'chart': data = pickle.loads(data)
		if dt:
			index = Data.findex(data,dt)
			data = data[:index+1]
		if bars:
			data = data[-bars:]
		if not pm:
			raise Exception('to code')
		return data
	
	def init_prev_close_cache(self):
		
		hash_data = self.redis_conn.hgetall('1d'+'chart')
		#return {field.decode(): pickle.loads(value) for field, value in hash_data.items()}
		for ticker, value in hash_data.items():
			value = json.loads(value)
			value = value[-1]['close']
			self.redis_conn.hset('prev_close', ticker, pickle.dumps(value))
			
	@staticmethod
	def fetch_stock_data(tickers):
		args = " ".join(tickers)
		ds = yf.download(args, interval='1m', period='1d', prepost=True, auto_adjust=True, threads=True, keepna=False)
		last_close_values = {}
		for ticker in tickers:
			close_data = ds['Close', ticker]
			close_data = close_data.dropna()
			if close_data.empty:
				pass
			else:
				last_non_na_close = close_data.iloc[-1]
				last_close_values[ticker] = last_non_na_close
		return last_close_values
	
	
	def get_current_prices(self):
		tickers = self.get_ticker_list()
		batches = []
		for i in range(0,len(tickers),1000):
			batches.append(tickers[i:i+ 1000])
		with multiprocessing.Pool(5) as pool:
			results = pool.map(self.fetch_stock_data,batches)
		return {k: v for d in results for k, v in d.items()}

	def get_ds(self,form = 'match',request='full',tf='1d', bars=0):
		returns = []
		
		if request == 'full':
			market_open = True#self.is_market_open()
			if market_open:
				self.init_prev_close_cache()
				current_prices = self.get_current_prices()
				for ticker, value in current_prices.items():
					self.redis_conn.hset('current_price', ticker, pickle.dumps(value))
			if form == 'screener':
				hash_data = self.redis_conn.hgetall(tf+form)
				#return {field.decode(): pickle.loads(value) for field, value in hash_data.items()}
				tickers = []
				for ticker, value in hash_data.items():
					try:
						ticker = ticker.decode()
						value = pickle.loads(value)
						if bars:
							padding = bars - value.shape[0]
							if padding > 0:
								pad_width = [(0, padding)] + [(0, 0)] * (value.ndim - 1)  # Pad only the first dimension
								value = np.pad(value, pad_width, mode='constant', constant_values=0)
						if market_open:
							value = value[-(bars-1):,:]
							try:
								price = current_prices[ticker]
								change = price/pickle.loads(self.redis_conn.hget('prev_close',ticker)) - 1
							except:
								change = 0
							value = np.vstack( [value,np.array([0] +[change for _ in range(4)])])
						else:
							value = value[-bars:,:]
							for ii in (2,3,4):
								value[-1,ii] = value[-1,1]
						returns.append(value)
						tickers.append(ticker)
					except TimeoutError: 
						pass
				return np.array(returns), tickers
			elif form == 'match':
				hash_data = self.redis_conn.hgetall(tf+form)
				#return {field.decode(): pickle.loads(value) for field, value in hash_data.items()}
				return [[field.decode(), pickle.loads(value)] for field, value in hash_data.items()]
		else:
			if form == 'trainer':
				classifications = []
				failed = 0
				for ticker, dt, classification in request:
					try:
						value = pickle.loads(self.redis_conn.hget(tf+'screener',ticker))#get rid of dt becuase dont need for training
						if not dt == '' or dt == None:
							index = Data.findex(value,dt)
							value = value[index-bars+1:index+1,:]
						value = value[:,1:]
						padding = bars - value.shape[0]
						if padding > 0:
							pad_width = [(0, padding)] + [(0, 0)] * (value.ndim - 1)  # Pad only the first dimension
							value = np.pad(value, pad_width, mode='constant', constant_values=0)
						returns.append(value)
						classifications.append(classification)
					except:
						failed += 1
				print(f'{failed} df requests failed!')
				returns = np.array(returns)
				classifications = np.array(classifications)
				return returns, classifications
			elif form == 'screener':
				tickers = []
				for ticker, dt in request:
					try:
						value = pickle.loads(self.redis_conn.hget(tf+form,ticker))
						if dt != '' and dt != None:
							try:
								index = Data.findex(value,dt)
								value = value[index-bars+1:index+1,:]
							except:
								raise TypeError
						else:
							value = value[-bars:]
						padding = bars - value.shape[0]
						if padding > 0:
							raise TypeError
							pad_width = [(padding,0)] + [(0, 0)] * (value.ndim - 1)  # Pad only the first dimension
							value = np.pad(value, pad_width, mode='constant', constant_values=0)
						for ii in (2,3,4):
							value[-1,ii] = value[-1,1]
						returns.append(value)
						tickers.append(ticker)
					except TypeError:
						pass
				returns = np.array(returns)
				return returns, tickers
	
	def findex(df, dt):
		dt = Data.format_datetime(dt)
		i = int(len(df)/2)		
		k = int(i/2)
		while k != 0:
			date = df[i,0]
			if date > dt:
				i -= k
			elif date < dt:
				i += k
			k = int(k/2)
		while df[i,0] < dt:
			i += 1
		while df[i,0] > dt:
			i -= 1
		return i
	
	def get_ticker_list(self, type='full'):
		cursor = self.mysql_conn.cursor(buffered=True)
		if type == 'full':
			query = "SELECT ticker FROM full_ticker_list"
			cursor.execute(query)
			data = cursor.fetchall()
			cursor.close()
			data = [item[0] for item in data]
			return data
		elif type == 'current':
			raise Exception('need current func. has to pull from tv or something god')###################################################################################################################################
	
	@staticmethod
	def format_datetime(dt,reverse=False):
		if reverse:
			return datetime.datetime.fromtimestamp(dt)
		if type(dt) == int or type(dt) == float:
			return dt
		if dt is None or dt == '': return None
		if dt == 'current': return datetime.datetime.now(pytz.timezone('EST'))
		if isinstance(dt, str):
			try: dt = datetime.datetime.strptime(dt, '%Y-%m-%d')
			except: dt = datetime.datetime.strptime(dt, '%Y-%m-%d %H:%M:%S')
		time = datetime.time(dt.hour, dt.minute, 0)
		dt = datetime.datetime.combine(dt.date(), time)
		if dt.hour == 0 and dt.minute == 0:
			time = datetime.time(9, 30, 0)
			dt = datetime.datetime.combine(dt.date(), time)
		dt = dt.timestamp()
		return dt

	@staticmethod
	def is_market_open():
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

	def set_setup_info(self,user_id,st,size=None,score=None):
		for val, ident in [[size,'sample_size'],[score,'score']]:
			if val != None:
				with self.mysql_conn.cursor(buffered=True) as cursor:
					query = f"UPDATE setups SET {ident} = %s WHERE user_id = %s AND name = %s;"
					cursor.execute(query, (val, user_id, st))
		self.mysql_conn.commit()
		
	def get_setup_info(self,user_id,st):
		with self.mysql_conn.cursor(buffered=True) as cursor:
			cursor.execute('SELECT tf,setup_length from setups WHERE user_id = %s AND name = %s',(user_id,st))
			return cursor.fetchall()[0]
		
	def get_finished_study_tickers(self,user_id,st):
		with self.mysql_conn.cursor(buffered = True) as cursor:
			query = "SELECT DISTINCT ticker FROM study WHERE user_id = %s AND st = %s"
			cursor.execute(query, (user_id, st))

			return [row[0] for row in cursor.fetchall()]

	def get_study_length(self,user_id,st):
		with self.mysql_conn.cursor(buffered = True) as cursor:
			query = "SELECT COUNT(*) FROM study WHERE user_id = %s AND st = %s AND annotation <> ''"
			cursor.execute(query, (user_id, st))
			count = cursor.fetchone()[0]
		return count
			
	def set_study(self,user_id,st,instances):
		with self.mysql_conn.cursor(buffered = True) as cursor:
			query = [[user_id,st,ticker,dt,''] for ticker,tf,dt in instances]
			cursor.executemany("INSERT INTO study VALUES (%s, %s, %s, %s, %s)",query)
		self.mysql_conn.commit()

	def get_setup_sample(self,user_id,st):
		with self.mysql_conn.cursor(buffered=True) as cursor:
			cursor.execute('SELECT setup_id, tf,setup_length from setups WHERE user_id = %s AND name = %s',(user_id,st))
			setup_id, tf,setup_length = cursor.fetchall()[0]
			cursor.execute('SELECT ticker,dt,value from setup_data WHERE setup_id = %s',(setup_id,))
			#values = [[ticker,dt,val] for setup_id,ticker,dt,val in cursor.fetchall()]
			values = cursor.fetchall()
			return values,tf,setup_length
		
	def set_setup_sample(self,user_id,st,data):##################################### ix this shit bruhhg dododosoosdodsfdsiho
		with self.mysql_conn.cursor(buffered=True) as cursor:
			cursor.execute('SELECT setup_id from setups WHERE user_id = %s AND name = %s',(user_id,st))
			setup_id = cursor.fetchone()[0]
			print(setup_id)
			query = [[setup_id,ticker,dt,classification] for ticker,dt,classification in data]
			cursor.executemany("INSERT INTO setup_data VALUES (%s, %s, %s,%s)", query)
		self.mysql_conn.commit()

