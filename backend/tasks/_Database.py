
import numpy as np
import  pandas as pd, numpy as np, datetime, mysql.connector, pytz, redis, pickle,  multiprocessing
from tqdm import tqdm
from collections import defaultdict
import yfinance as yf

class Cache:

	def get_hash(self, parent_key,child_key = None):
		if child_key: 
			hash_data = self.r.hget(parent_key,child_key)
			return pickle.loads(hash_data)
		else:  
			hash_data = self.r.hgetall(parent_key)
			return {field.decode(): pickle.loads(value) for field, value in pickle.loads(hash_data).items()}

	def set_hash(self, data, parent_key):
		for child_key, item in data.items():
			serialized_item = pickle.dumps(item)
			self.r.hset(parent_key, child_key, serialized_item)

	def get(self, key):
		serialized_data = self.r.get(key)
		return pickle.loads(serialized_data)

	def set(self, data, key):
		serialized_data = pickle.dumps(data)
		self.r.set(key, serialized_data)

	def __init__(self,conn=None):
		self.type = 'redis'
		if conn:
			self.r = conn
		else:
			try:
				self.r = redis.Redis(host='redis', port=6379)
				self.r.ping()
			except Exception as e:
				try:
					self.r = redis.Redis(host='127.0.0.1', port=6379)
					self.r.ping()
					print('External Redis')
				except Exception as e:
					raise Exception('Redis Connection Failed')

class Database:
	
	def __init__(self,conn=None):
		self.type = 'sql'
		if conn:
			self._conn = conn
		else:
			try:
				self._conn = mysql.connector.connect(host='mysql',port='3306',user='root',password='7+WCy76_2$%g',database='broker')
			except:
				try:
					self._conn = mysql.connector.connect(host='localhost',port='3307',user='root',password='7+WCy76_2$%g',database='broker')
					print('External Data')
				except:
					print('broker database doesnt exist so trying to setup')
					self._conn = mysql.connector.connect(host='localhost',port='3307',user='root',password='7+WCy76_2$%g')
					self.setup()
	
	def get_ticker_list(self, type='full'):
		cursor = self._conn.cursor(buffered=True)
		if type == 'full':
			query = "SELECT ticker FROM full_ticker_list"
			cursor.execute(query)
			data = cursor.fetchall()
			cursor.close()
			data = [item[0] for item in data]
			return data
		elif type == 'current':
			raise Exception('need current func. has to pull from tv or something god')###################################################################################################################################
	# def get_df(self, ticker, tf='1d', dt=None, bars=0, pm=True):
	# 	cursor = self._conn.cursor(buffered=True)
	# 	if dt != None:
	# 		dt = Database.format_datetime(dt)
	# 		query = "SELECT dt, open, high, low, close, volume FROM dfs WHERE ticker = %s AND tf = %s ORDER BY dt ASC"
	# 		cursor.execute(query, (ticker, tf, dt))
	# 	else:
	# 		query = "SELECT dt, open, high, low, close, volume FROM dfs WHERE ticker = %s AND tf = %s ORDER BY dt ASC"
	# 		cursor.execute(query, (ticker, tf))
		
	# 	data = cursor.fetchall()
	# 	if bars != 0:
	# 		return np.array(data[-bars:])
	# 	return np.array(data)#####new
	def match_format(data):
		length = len(data)
		d = np.zeros((length-1, 4))
		for i in range(1, length):
			close = data[i,4]
			d[i-1] = [close, (close/data[i-1,4]) - 1, data[i, 5], data[i, 0]]
		return d

	def get_df(self, tf,ticker,format='normal'):#, tf='1d', dt=None, bars=0, pm=True):

		cursor = self._conn.cursor(buffered=True)
		query = "SELECT dt, open, high, low, close, volume FROM dfs WHERE ticker = %s AND tf = %s"
		print(ticker,tf)
		cursor.execute(query, (ticker, tf))
		data = np.array(cursor.fetchall())
		if format == 'match':
			data = Database.match_format(data)
		#print(data)
		#data = data[data[:, 0].argsort()]
		#data = Database.process_ticker_data(ticker,tf,dt,data)
		#if bars != 0:
			#return np.array(data[-bars:])
		return data

	def get_ds(self,tf,format='normal'):
		start = datetime.datetime.now()
		cursor = self._conn.cursor(buffered=True)
		query = "SELECT ticker, dt, open, high, low, close, volume FROM dfs WHERE tf = %s"
		cursor.execute(query,(tf,))
		data = cursor.fetchall()
		print(datetime.datetime.now() - start, flush = True)
		organized_data = defaultdict(list)
		for row in data:
			organized_data[row[0]].append(row[1:])

		with multiprocessing.Pool() as pool:
			results = pool.starmap(Database.process_ticker_data, [(format, organized_data[ticker]) for ticker in organized_data])
			data_dict = dict(zip(organized_data.keys(), results))

		return data_dict

	def process_ticker_data(format, data):
		data = np.array(data)
		if format == 'match':
			data = Database.match_format(data)
			
		#return data[data[:, 0].argsort()]
		

	def get_user(self,email,password):
		with self._conn.cursor(buffered=True) as cursor:
			cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
			user_data = cursor.fetchone()
			if len(user_data) > 0:
				if password == user_data[2]:
					return user_data[0]
	
	def set_user(self, user_id = None, email=None, password=None, settings_string=None,delete = False):
		with self._conn.cursor(buffered=True) as cursor:
			if user_id is not None:
				if not delete:
					fields = []
					values = []
					if email is not None:
						fields.append("email = %s")
						values.append(email)
					if password is not None:
						fields.append("password = %s")
						values.append(password)
					if settings_string is not None:
						fields.append("settings = %s")
						values.append(settings_string)
					if fields:
						update_query = f"UPDATE users SET {', '.join(fields)} WHERE id = %s"
						values.append(user_id)  
						cursor.execute(update_query, values)
						self._conn.commit()
				else:
					cursor.execute("DELETE FROM users WHERE id = %s",(user_id,))
			else:
				insert_query = "INSERT INTO users (email, password, settings) VALUES (%s, %s, %s)"
				cursor.execute(insert_query, (email, password, settings_string if settings_string is not None else ''))
				self._conn.commit()
				
	def get_settings(self,user_id):
		with self._conn.cursor(buffered=True) as cursor:
			cursor.execute("SELECT settings FROM users WHERE id = %s", (user_id,))
			return cursor.fetchone()[0]


	def get_model(self,user_id,st=None):
		with self._conn.cursor(buffered=True) as cursor:
			if st is None:
				cursor.execute('SELECT model from setups WHERE user_id = %s AND name = %s',(user_id,st))
			else:
				cursor.execute('SELECT model from setups WHERE user_id = %s',(user_id,))
			return cursor.fetchone()[0]
		
	def set_model(self,user_id):
		pass

	def set_setup(self,user_id,st,tf):
		with self._conn.cursor(buffered=True) as cursor:
			insert_query = "INSERT INTO setups (user_id, name, tf, model) VALUES (%s, %s, %s, %s)"
			cursor.execute(insert_query, (user_id,st,tf,''))
		self._conn.commit()
		
	def get_sample(self,user_id,st):
		with self._conn.cursor(buffered=True) as cursor:
			cursor.execute('SELECT setup_id from setups WHERE user_id = %s AND name = %s',(user_id,st))
			setup_id = cursor.fetchone()[0]
			cursor.execute('SELECT * from setup_data WHERE setup_id = %s',(setup_id,))
			return cursor.fetchall()
		
	def set_sample(self,user_id,st,ticker,dt,value):##################################### ix this shit bruhhg dododosoosdodsfdsiho
		with self._conn.cursor(buffered=True) as cursor:
			cursor.execute('SELECT setup_id from setups WHERE user_id = %s AND name = %s',(user_id,st))
			setup_id = cursor.fetchone()[0]
			cursor.execute("INSERT IGNORE INTO setup_data VALUES (%s, %s, %s)", (setup_id,ticker,dt))
			
		self._conn.commit()

	def update(self,force_retrain=False):

		with self._conn.cursor(buffered=True) as cursor:

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
		
			ticker_list = self.get_ticker_list('full')

		
			for ticker in tqdm(ticker_list):
				for tf in ['1d']:
					try:
						if tf == '1d':
						
							ytf = '1d'
							period = '25y'
						elif tf == '1min':
							ytf = '1m'
							period = '5d'
						else:
							raise Exception('invalid timeframe to update')
						ydf = yf.download(tickers = ticker, period = period, group_by='ticker', interval = ytf, ignore_tz = True, progress=False, show_errors = False, threads = True, prepost = True) 
						ydf.drop(axis=1, labels="Adj Close",inplace = True)
						ydf.dropna(inplace = True)
						if Database.is_market_open() == 1: ydf.drop(ydf.tail(1).index,inplace=True)
						ydf.index = ydf.index.normalize() + pd.Timedelta(minutes = 570)
						ydf.index = (ydf.index.astype(np.int64) // 10**9)
						cursor.execute("SELECT MAX(dt) FROM dfs WHERE ticker = %s AND tf = %s", (ticker, tf))
						result = cursor.fetchone()
						last_day = result[0] if result else 0
					
						if type(last_day) == int:
							index = findex(ydf, last_day) 
							ydf = ydf[index + 1:]
						ydf.reset_index(inplace = True)
					
						ydf = ydf.values.tolist()
						ydf = [[ticker, tf] + row for row in ydf]
						insert_query = """
						INSERT INTO dfs (ticker, tf, dt, open, high, low, close, volume) 
						VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
						ON DUPLICATE KEY UPDATE 
						open = VALUES(open), 
						high = VALUES(high), 
						low = VALUES(low), 
						close = VALUES(close), 
						volume = VALUES(volume)
						"""
						cursor.executemany(insert_query, ydf)
						self._conn.commit()
					
					except Exception as e:
						print(f'{ticker} failed: {e}')
						print(ydf)

	def close_connection(self):
		self._conn.close()

	def setup(self):
		if input('Override database data? y/n') != 'y':
			return
		with self._conn.cursor(buffered=True) as cursor:
			cursor.execute("CREATE DATABASE IF NOT EXISTS broker DEFAULT CHARACTER SET 'utf8';")
			self._conn.commit()
			cursor.execute("USE broker;")
			self._conn.commit()
			sql_commands = """
			DROP TABLE IF EXISTS setup_data;
			DROP TABLE IF EXISTS setups;
			DROP TABLE IF EXISTS users;
			DROP TABLE IF EXISTS dfs;
			DROP TABLE IF EXISTS full_ticker_list;
			DROP TABLE IF EXISTS current_ticker_list;
			CREATE TABLE dfs(
				ticker VARCHAR(5) NOT NULL,
				tf VARCHAR(3) NOT NULL,
				dt INT NOT NULL,
				open FLOAT,
				high FLOAT,
				low FLOAT,
				close FLOAT,
				volume FLOAT,
				PRIMARY KEY (ticker, tf, dt)
			);
			CREATE INDEX ticker_index ON dfs (ticker);
			CREATE INDEX tf_index ON dfs (tf);
			CREATE INDEX dt_index ON dfs (dt);
			CREATE TABLE users(
				id INT AUTO_INCREMENT PRIMARY KEY,
				email VARCHAR(255) NOT NULL UNIQUE,
				password VARCHAR(255),
				settings TEXT
			);
			CREATE INDEX email_index ON users(email);
			CREATE TABLE setups(
				user_id INT NOT NULL,
				name VARCHAR(255) NOT NULL,
				setup_id INT AUTO_INCREMENT UNIQUE,
				tf VARCHAR(3) NOT NULL,
				model BINARY,
				UNIQUE(user_id, name),
				FOREIGN KEY (user_id) REFERENCES users(id)
			);
			CREATE INDEX user_id_index ON setups (user_id);
			CREATE INDEX name_index ON setups (name);
			CREATE TABLE setup_data(
				setup_id INT NOT NULL,
				ticker VARCHAR(5) NOT NULL,
				dt INT NOT NULL,
				value BOOLEAN NOT NULL,
				UNIQUE(ticker, dt),
				FOREIGN KEY (setup_id) REFERENCES setups(setup_id)
			);
			CREATE INDEX id_index ON setup_data (setup_id);
			CREATE TABLE full_ticker_list(ticker VARCHAR(5) NOT NULL);
			CREATE TABLE current_ticker_list(ticker VARCHAR(5) NOT NULL);
			"""
			commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
			for command in commands:cursor.execute(command)
			df = pd.read_feather("C:/dev/Broker/old/sync/files/full_scan.feather")
			df = df['ticker'].tolist()
			df = [[x] for x in df]
			insert_query = "INSERT INTO full_ticker_list VALUES (%s)"
			cursor.executemany(insert_query, df)
			self._conn.commit()
			if True:
				
				for tf in ['1d']:
					args = [[ticker, tf, 'C:/dev/broker/old/' + tf + '/' + ticker + '.feather'] for ticker in self.get_ticker_list()]
					for ticker, tf, path in tqdm(args,desc='Transfering Dataframes'):
						try:
							df = pd.read_feather(path)
							df['datetime']= (df['datetime'].astype(np.int64) // 10**9)
							df = df.values.tolist()
							rows = [[ticker, tf] + row for row in df]
							insert_query = "INSERT IGNORE INTO dfs VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
							cursor.executemany(insert_query, rows)
							self._conn.commit()
						except Exception as e: #if d doesnt exist or theres no data then this gets hit every loop
							print(e)
		self.update()
	
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
	

	def train(self, st, use, epochs): 
		db.consolidate_database()
		allsetups = pd.read_feather('local/data/' + st + '.feather').sort_values(
			by='dt', ascending=False).reset_index(drop=True)
		yes = []
		no = []
		groups = allsetups.groupby(pd.Grouper(key='ticker'))
		dfs = [group for _, group in groups]
		for df in dfs:
			df = df.reset_index(drop=True)
			for i in range(len(df)):
				bar = df.iloc[i]
				if bar['value'] == 1:
					for ii in [i + ii for ii in [-2, -1, 1, 2]]:
						if abs(ii) < len(df):
							bar2 = df.iloc[ii]
							if bar2['value'] == 0:
								no.append(bar2)
					yes.append(bar)
		yes = pd.DataFrame(yes)
		no = pd.DataFrame(no)
		required = int(len(yes) - ((len(no)+len(yes)) * use))
		if required < 0:
			no = no[:required]
		while True:
			no = no.drop_duplicates(subset=['ticker', 'dt'])
			required = int(len(yes) - ((len(no)+len(yes)) * use))
			sample = allsetups[allsetups['value'] == 0].sample(frac=1)
			if required < 0 or len(sample) == len(no):
				break
			sample = sample[:required + 1]
			no = pd.concat([no, sample])
		df = pd.concat([yes, no]).sample(frac=1).reset_index(drop=True)
		df['tf'] = st.split('_')[0]
		df = df[['ticker', 'dt', 'tf']]
		
		return df
		df = pd.read_feather('local/data/' + st + '.feather')
		ones = len(df[df['value'] == 1])
		if ones < 150:
			return
		x = self.raw_np
		y = self.y_np

		model = Sequential([Bidirectional(LSTM(64, input_shape=(x.shape[1], x.shape[2]), return_sequences=True,),), Dropout(
			0.2), Bidirectional(LSTM(32)), Dense(3, activation='softmax'),])
		model.compile(loss='sparse_categorical_crossentropy',
					  optimizer=Adam(learning_rate=1e-3), metrics=['accuracy'])
		model.fit(x, y, epochs=epochs, batch_size=64, validation_split=.2,)
		model.save('sync/models/model_' + st)
		tensorflow.keras.backend.clear_session()