import numpy as np
import  pandas as pd, numpy as np, datetime, mysql.connector, pytz, redis, pickle,  multiprocessing
import numpy as np
import  pandas as pd, os, numpy as np, time,datetime, mysql.connector, pytz, redis, pickle,  multiprocessing, json
from tqdm import tqdm
from collections import defaultdict
import yfinance as yf
import asyncio
from mysql.connector import errorcode
import aiomysql, aioredis

import multiprocessing
import redis
import mysql.connector
from contextlib import closing



class Data:
	


	#eng_project
	def __init__(self):
		try:
			self.inside_container = os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False)
			if self.inside_container: #inside container
				self.r = redis.Redis(host='redis', port=6379)
				while True: #wait for redis to be ready
					try:
						if not self.r.info()['loading'] == 0: raise Exception('gosh')
						self.r.ping()
						break
					except:
						print('waiting for redis',flush=True)
						time.sleep(1)
				while True:
					try:
						self._conn = mysql.connector.connect(host='mysql',port='3306',user='root',password='7+WCy76_2$%g',database='broker')
						break
					except mysql.connector.errors.DatabaseError as e:
						if (e.errno != errorcode.ER_ACCESS_DENIED_ERROR
						and e.errno != errorcode.ER_BAD_DB_ERROR):
							print('waiting for mysql',flush=True)
							time.sleep(1)
						else:
							raise Exception(e)
			else:
				self._conn = mysql.connector.connect(host='localhost',port='3307',user='root',password='7+WCy76_2$%g',database='broker')
				self.r = redis.Redis(host='127.0.0.1', port=6379)
		except:
			self._conn = mysql.connector.connect(host='localhost',port='3307',user='root',password='7+WCy76_2$%g')
			self.setup()
			
	def get_trainer_queue_size(self,user_id,st):
		return self.r.llen(str(user_id)+st)

	def set_trainer_queue(self, user_id,st, instance):
		# Add the item to the Redis list
		self.r.lpush(str(user_id)+st, json.dumps(instance))

	def get_df(self, form='chart', ticker='QQQ', tf='1d', dt=None, bars=0, pm=True):
		#async with self.redis_pool.get() as conn:
			
		data = self.r.hget(tf+form,ticker)
		if not form == 'chart': data = pickle.loads(data)
		if dt:
			index = Data.findex(data,dt)
			data = data[:index+1]
		if bars:
			data = data[-bars:]
		if not pm:
			raise Exception('to code')
		return data
	




	# Assuming you have defined screener_format function here
	@staticmethod
	def process_ticker_data(bar):
		try:
			ticker,tf = bar
			with sql_pool.get_connection() as conn:
					
				with conn.cursor() as cursor:
					cursor.execute("SELECT dt, open, high, low, close, volume FROM dfs WHERE ticker = %s and tf = %s", (ticker,tf))
					data = np.array(cursor.fetchall())

					# Process data
					#print(data,flush=True)
					for form in ('screener','chart','match'):
						if form == 'screener':
							dt = data[1:,0]
							dt = dt.reshape(-1,1)
							normalized_data = (data[1:,1:5] / data[:-1,4][:, None]) - 1
							normalized_data = np.column_stack((dt,normalized_data))
							processed_data = pickle.dumps(normalized_data)
						elif form == 'match':
							#dt, open, high, low, close, volume 
							# 0    1     2     3     4      5
							ohlcData = data[1:,1:5]/data[:-1, 4].reshape(-1, 1) - 1
							mean = np.mean(ohlcData, axis=0)
							std = np.std(ohlcData, axis=0)
							ohlcData = (ohlcData - mean) / std
			
							processed_data = pickle.dumps(np.column_stack((data[1:, 0], data[1:, 4], ohlcData[:, 0], ohlcData[:, 1], ohlcData[:, 2], ohlcData[:, 3], data[1:, 5])))
							#close_prices = data[:, 4]
							#return pickle.dumps(np.column_stack((data[1:, 0], close_prices[1:], (data[1:, 1] / close_prices[:-1] - 1), (data[1:, 2]/close_prices[:-1] -1), (data[1:,3]/close_prices[:-1] - 1), (close_prices[1:] / close_prices[:-1]) - 1, data[1:, 5])))
		
						elif form == 'chart':
							list_of_lists = data.tolist()[:]
							if 'd' in tf or 'w' in tf:
								list_of_lists = [{
								'time': pd.to_datetime(row[0], unit='s').strftime('%Y-%m-%d'),
								'open': row[1],
								'high': row[2],
								'low': row[3],
								'close': row[4]
							} for row in list_of_lists]
							else:
								list_of_lists = [{
								'time': pd.to_datetime(row[0], unit='s').strftime('%Y-%m-%d %H:%M:%S'),
								'open': row[1],
								'high': row[2],	
								'low': row[3],
								'close': row[4]
								}for row in list_of_lists]
					
							processed_data = json.dumps(list_of_lists)
						redis_pool.hset(tf+form, ticker, processed_data)
		except TimeoutError:
			pass

	# Main Function
	def init_cache(self,force = False):
		if not force and self.r.exists('working'):
			print('assuming redis already populated',flush = True)
			return
		global sql_pool
		sql_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=12, host='mysql',port='3306',user='root',password='7+WCy76_2$%g',database='broker')
		global redis_pool
		redis_pool = self.r#redis.ConnectionPool(host='localhost', port=6379)
		tickers = self.get_ticker_list()# get_unique_tickers()  # Define this function to get tickers from your DB
		pool = multiprocessing.Pool(processes=8)  # Adjust number of processes as needed
		self.r.set('working','working')
		for tf in ('1d',):
			arglist = [[ticker,tf] for ticker in tickers]
			pool.map(self.process_ticker_data, arglist)
		pool.close()
		pool.join()
		
	
	def get_ds(self,form = 'match',request='full',tf='1d', bars=0):
		
		if request == 'full':
			if bars != 0:
				raise Exception('to code')
			hash_data = self.r.hgetall(tf+form)
			#return {field.decode(): pickle.loads(value) for field, value in hash_data.items()}
			return [[field.decode(), pickle.loads(value)] for field, value in hash_data.items()]
			

		else:
			returns = []
			


			if form == 'trainer':
				classifications = []
				failed = 0
				for ticker, dt, classification in request:
					try:
						value = pickle.loads(self.r.hget(tf+'screener',ticker))#get rid of dt becuase dont need for training
					
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
						value = pickle.loads(self.r.hget(tf+form,ticker))
						if dt != '' and dt != None:
							try:
								index = Data.findex(value,dt)
								value = value[index-bars+1:index+1,:]
							except:
								raise TypeError
						else:
							value = value[-bars:]
						#print(value.shape)
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
						#print(ticker,dt)
			

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
		#return dt
		dt = dt.timestamp()
		return dt

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


	def set_setup_info(self,user_id,st,size=None,score=None):
		for val, ident in [[size,'sample_size'],[score,'score']]:
			if val != None:
				with self._conn.cursor(buffered=True) as cursor:
					query = f"UPDATE setups SET {ident} = %s WHERE user_id = %s AND name = %s;"
					cursor.execute(query, (val, user_id, st))
		self._conn.commit()
		
	def get_setup_info(self,user_id,st):
		with self._conn.cursor(buffered=True) as cursor:
			cursor.execute('SELECT tf,setup_length from setups WHERE user_id = %s AND name = %s',(user_id,st))
			return cursor.fetchall()[0]
		
	
	def get_setup_sample(self,user_id,st):
		with self._conn.cursor(buffered=True) as cursor:
			cursor.execute('SELECT setup_id, tf,setup_length from setups WHERE user_id = %s AND name = %s',(user_id,st))
			setup_id, tf,setup_length = cursor.fetchall()[0]
			cursor.execute('SELECT ticker,dt,value from setup_data WHERE setup_id = %s',(setup_id,))
			#values = [[ticker,dt,val] for setup_id,ticker,dt,val in cursor.fetchall()]
			values = cursor.fetchall()
			return values,tf,setup_length
		
	
		
	def set_setup_sample(self,user_id,st,data):##################################### ix this shit bruhhg dododosoosdodsfdsiho
		with self._conn.cursor(buffered=True) as cursor:
			cursor.execute('SELECT setup_id from setups WHERE user_id = %s AND name = %s',(user_id,st))
			setup_id = cursor.fetchone()[0]
			print(setup_id)
			query = [[setup_id,ticker,dt,classification] for ticker,dt,classification in data]
			#cursor.executemany("INSERT IGNORE INTO setup_data VALUES (%s, %s, %s,%s)", query)
			cursor.executemany("INSERT INTO setup_data VALUES (%s, %s, %s,%s)", query)
			
		self._conn.commit()

	def update(self,force_retrain=False):

		with self._conn.cursor(buffered=True) as cursor:

			def findex(df, dt):
				dt = Data.format_datetime(dt)
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
						if Data.is_market_open() == 1: ydf.drop(ydf.tail(1).index,inplace=True)
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
						
		self.init_cache()

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
			CREATE TABLE watchlists (
    user_id INT,
    name VARCHAR(255) NOT NULL,
    ticker VARCHAR(5) NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(id)
    ON DELETE CASCADE
);

CREATE INDEX user_id_index ON watchlists (user_id);
CREATE INDEX name_index ON watchlists (name);
			CREATE TABLE setups(
				user_id INT NOT NULL,
				name VARCHAR(255) NOT NULL,
				setup_id INT AUTO_INCREMENT UNIQUE,
				tf VARCHAR(3) NOT NULL,
				setup_length INT NOT NULL,
				UNIQUE(user_id, name),
				FOREIGN KEY (user_id) REFERENCES users(id)
				ON DELETE CASCADE
			);
			CREATE INDEX user_id_index ON setups (user_id);
			CREATE INDEX name_index ON setups (name);
			CREATE TABLE setup_data(
				setup_id INT NOT NULL,
				ticker VARCHAR(5) NOT NULL,
				dt INT NOT NULL,
				value BOOLEAN NOT NULL,
				UNIQUE(setup_id,ticker, dt),
				FOREIGN KEY (setup_id) REFERENCES setups(setup_id)
				ON DELETE CASCADE
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
							insert_query = "INSERT INTO dfs VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
							cursor.executemany(insert_query, rows)
							self._conn.commit()
						except Exception as e: #if d doesnt exist or theres no data then this gets hit every loop
							print(e)
		self.update()
	

data = Data()
