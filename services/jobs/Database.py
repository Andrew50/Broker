import numpy as np
import  pandas as pd, numpy as np, datetime, mysql.connector, pytz, redis, pickle,  multiprocessing
import numpy as np
import  pandas as pd, os, numpy as np, time,datetime, mysql.connector, pytz, redis, pickle,  multiprocessing, json
import yfinance as yf
from mysql.connector import errorcode

import multiprocessing
import redis
import mysql.connector




class Database:


	def __init__(self):

		redis_conn = redis.Redis(host='redis', port=6379)
		mysql_conn = mysql.connector.connect(host='mysql',port='3306',user='root',password='7+WCy76_2$%g',database='broker')
#redis_conn = mysql.connector.connect(host='mysql',port='3306',user='root',password='7+WCy76_2$%g',database='broker')



		self.r = redis_conn
		self._conn = mysql_conn 
		



		# self.inside_container = os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False)
		# try:
		# 	if self.inside_container: #inside container
		# 		self.r = redis.Redis(host='redis', port=6379)
		# 		while True: #wait for redis to be ready
		# 			try:
		# 				if not self.r.info()['loading'] == 0: raise Exception('gosh')
		# 				self.r.ping()
		# 				break
		# 			except:
		# 				print('waiting for redis',flush=True)
		# 				time.sleep(1)
		# 		while True:
		# 			try:
		# 				self._conn = mysql.connector.connect(host='mysql',port='3306',user='root',password='7+WCy76_2$%g',database='broker')
		# 				break
		# 			except mysql.connector.errors.DatabaseError as e:
		# 				if (e.errno != errorcode.ER_ACCESS_DENIED_ERROR
		# 				and e.errno != errorcode.ER_BAD_DB_ERROR):
		# 					print('waiting for mysql',flush=True)
		# 					time.sleep(1)
		# 				else:
		# 					raise Exception(e)
		# 	else:
		# 		self._conn = mysql.connector.connect(host='localhost',port='3307',user='root',password='7+WCy76_2$%g',database='broker')
		# 		self.r = redis.Redis(host='127.0.0.1', port=6379)
		

		# except:
		# 	self._conn = mysql.connector.connect(host='localhost',port='3307',user='root',password='7+WCy76_2$%g')
		# 	self.r = redis.Redis(host='127.0.0.1', port=6379)
		# 	self.setup()
		

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
		#if not force and self.r.exists('working'):
		#	print('assuming redis already populated',flush = True)
			#return
		global sql_pool
		#if self.inside_container:
		if True:
			sql_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=12, host='mysql',port='3306',user='root',password='7+WCy76_2$%g',database='broker')
		else:
			sql_pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=12, host='localhost',port='3307',user='root',password='7+WCy76_2$%g',database='broker')
			
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



	####to remove once method for pulling current ticker list exists
	def get_ticker_list(self, type='full'):
		pd.read_csv('ticker_list.csv')
		return pd.read_csv('ticker_list.csv')['ticker'].tolist()
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
	



	def update(self,force_retrain=False,num = None):

		with self._conn.cursor(buffered=True) as cursor:

			def findex(df, dt):
				dt = self.format_datetime(dt)
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
			

			full_ticker_list = self.get_ticker_list()

			# full_ticker_list = ?
			# df = [[x] for x in full_ticker_list]
			# insert_query = "INSERT IGNORE INTO full_ticker_list VALUES (%s)"
			# cursor.executemany(insert_query, df)
			
				
		
			for ticker in full_ticker_list:
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
						ydf = yf.download(tickers = ticker, period = period, group_by='ticker', interval = ytf, ignore_tz = True, auto_adjust=True, progress=False, show_errors = False, threads = True, prepost = True) 
						#print(ydf)
						#ydf.drop(axis=1, labels="Adj Close",inplace = True)
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

	def close_connection(self):
		self._conn.close()

	def setup(self):

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
				ON DELETE CASCADE,
				UNIQUE(user_id,name)
			);

			CREATE INDEX user_id_index ON watchlists (user_id);
			CREATE INDEX name_index ON watchlists (name);


			CREATE TABLE study (
				user_id INT,
				st VARCHAR(255) NOT NULL,
				ticker VARCHAR(5) NOT NULL,
				dt INT NOT NULL,
				annotation TEXT,
				FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
				UNIQUE(user_id, st)
			) ;
			CREATE INDEX user_id_index ON study (user_id);
			CREATE INDEX st_index ON study (st);
			CREATE TABLE setups(
				user_id INT NOT NULL,
				name VARCHAR(255) NOT NULL,
				setup_id INT AUTO_INCREMENT UNIQUE,
				tf VARCHAR(3) NOT NULL,
				setup_length INT NOT NULL,
				sample_size INT,
				score INT,
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
			CREATE TABLE full_ticker_list(ticker VARCHAR(5) NOT NULL UNIQUE);
			"""
			commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
			for command in commands:cursor.execute(command)
			
			self._conn.commit()
		
db = Database()

if __name__ == "__main__":
	db.update()
	db.init_cache()
	db.close_connection()

