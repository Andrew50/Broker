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





class Data:
	
	def __init__(self):
		try:
			self.inside_container = os.environ.get('AM_I_IN_A_DOCKER_CONTAINER', False)
			if self.inside_container: #inside container
				self.r = redis.Redis(host='redis', port=6379)
				while True: #wait for redis to be ready
					try:
						if not self.r.info()['loading'] == 0: raise Exception('gosh')
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

	async def init_async_conn(self):
		try: 
			self.r_async
			return
		except:
			pass
		if self.inside_container: self._conn_async = await aiomysql.connect(host='mysql', port=3306, user='root', password='7+WCy76_2$%g', db='broker')
		else: self._conn_async = await aiomysql.connect(host='localhost', port=3307, user='root', password='7+WCy76_2$%g', db='broker')
		redis_host = 'redis' if self.inside_container else '127.0.0.1'
		self.r_async = aioredis.Redis(host=redis_host, port=6379)

	def init_cache(self,debug = False,force = True):
		if not force and self.r.exists('working'):
			print('assuming redis already populated',flush = True)
			return
		
		def match_format(data):
			# dt, open, high, low, close, volume 
			# 0    1     2     3     4      5
			ohlcData = data[1:,1:5]/data[:-1, 4].reshape(-1, 1) - 1
			mean = np.mean(ohlcData, axis=0)
			std = np.std(ohlcData, axis=0)
			ohlcData = (ohlcData - mean) / std
			
			return pickle.dumps(np.column_stack((data[1:, 0], data[1:, 4], ohlcData[:, 0], ohlcData[:, 1], ohlcData[:, 2], ohlcData[:, 3], data[1:, 5])))
			#close_prices = data[:, 4]
			#return pickle.dumps(np.column_stack((data[1:, 0], close_prices[1:], (data[1:, 1] / close_prices[:-1] - 1), (data[1:, 2]/close_prices[:-1] -1), (data[1:,3]/close_prices[:-1] - 1), (close_prices[1:] / close_prices[:-1]) - 1, data[1:, 5])))
		
		def screener_format(data):
			dt = data[:,0]

			data = data[:,1:5]
			mean = np.mean(data, axis=0)
			std = np.std(data, axis=0)
			data = (data - mean) / std

			#dt = data[1:,0]

			# data = (data[1:,:5] / data[:-1,:5]) - 1
			return pickle.dumps(np.column_stack((dt,data)))

		def chart_format(data,tf):
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
	
			r = json.dumps(list_of_lists)
			return r
		
		def set_hash(data, tf, form):
			for ticker, df in data.items():
				if tf in df:  # Check if tf data exists for the ticker
					try:
						if form == 'match':
							formatted_data = match_format(np.array(df[tf])) 
						elif form == 'screener':
							formatted_data = screener_format(np.array(df[tf]))
						elif form =='chart':
							formatted_data = chart_format(np.array(df[tf]),tf)
						self.r.hset(tf + form, ticker, formatted_data)
					except Exception as e:
						print(e + ' _ ' + form)
		
		cursor = self._conn.cursor(buffered=True)
		if debug:
			cursor.execute("SELECT COUNT(*) FROM dfs")
			total_count = cursor.fetchone()[0]
			limit = int(total_count * 0.05)
			cursor.execute(f"SELECT * FROM dfs LIMIT {limit}")
		else:
			cursor.execute("SELECT * FROM dfs")
		data = cursor.fetchall()
		
		organized_data = defaultdict(lambda: defaultdict(list))
		for row in data:
			ticker, tf, *rest = row
			organized_data[ticker][tf].append(rest)

		for ticker in organized_data:
			for tf in organized_data[ticker]:
				organized_data[ticker][tf] = np.array(organized_data[ticker][tf], dtype=float)
		for tf in ('1d',):#'1'):
			#for typ in ('match'): # for typ in ('match', 'chart', 'screener')
			set_hash(organized_data, tf, 'match')
				
		self.r.set('working','working')

	async def get_df(self, form='chart', ticker='QQQ', tf='1d', dt=None, bars=0, pm=True):
		data = await self.r_async.hget(tf+form,ticker)
		if not form == 'chart': data = pickle.loads(data)
		if dt:
			index = Data.findex(data,dt)
			data = data[:index+1]
		if bars:
			data = data[-bars:]
		if not pm:
			raise Exception('to code')
		return data
	
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
				
				for ticker, dt, classification in request:
					try:
						value = pickle.loads(self.r.hget(tf+'screener',ticker))
						if not dt == '' or dt == None:
							index = Data.findex(value,dt)
							value = value[index-bars+1:index+1,:]
						#print(value.shape)
						padding = bars - value.shape[0]
						if padding > 0:
							raise TypeError
							pad_width = [(0, padding)] + [(0, 0)] * (value.ndim - 1)  # Pad only the first dimension
							value = np.pad(value, pad_width, mode='constant', constant_values=0)
						returns.append(value)
						classifications.append(classification)
					except TypeError:
						pass
						#print(ticker,dt)
			

				returns = np.array(returns)
				classifications = np.array(classifications)
				return returns, classifications
			
			elif form == 'screener':
				tickers = []
				for ticker, dt in request:
					try:
						value = pickle.loads(self.r.hget(tf+form,ticker))
						if dt != '' and dt != None:
							index = Data.findex(value,dt)
							value = value[index-bars+1:index+1,:]
						else:
							value = value[-bars:]
						#print(value.shape)
						padding = bars - value.shape[0]
						if padding > 0:
							raise TypeError
							pad_width = [(0, padding)] + [(0, 0)] * (value.ndim - 1)  # Pad only the first dimension
							value = np.pad(value, pad_width, mode='constant', constant_values=0)
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


	async def get_user(self, email, password):
		async with self._conn_async.cursor() as cursor:
			await cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
			user_data = await cursor.fetchone()
			if user_data and len(user_data) > 0:
				if password == user_data[2]:  # Assuming password is at index 2
					return user_data[0]   
				
	
	
	async def set_user(self, user_id=None, email=None, password=None, settings_string=None, delete=False):
		async with self._conn_async.cursor() as cursor:
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
						await cursor.execute(update_query, values)
				else:
					await cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
			else:
				insert_query = "INSERT INTO users (email, password, settings) VALUES (%s, %s, %s)"
				await cursor.execute(insert_query, (email, password, settings_string if settings_string is not None else ''))

			await self._conn_async.commit()
				
	async def get_settings(self,user_id):
		async with self._conn_async.cursor() as cursor:
			await cursor.execute("SELECT settings FROM users WHERE id = %s", (user_id,))
			settings = await cursor.fetchone()
			return settings[0]
		
	async def get_user_setups(self,user_id):
		async with self._conn_async.cursor() as cursor:
			await cursor.execute("SELECT name, tf, setup_length from setups WHERE user_id = %s",(user_id,))
			return await cursor.fetchall()
		


	# def get_model(self,user_id,st=None):
	# 	with self._conn.cursor(buffered=True) as cursor:
	# 		if st is None:
	# 			cursor.execute('SELECT tf,model from setups WHERE user_id = %s AND name = %s',(user_id,st))
	# 		else:
	# 			cursor.execute('SELECT tf,model from setups WHERE user_id = %s',(user_id,))
	# 		cursor.fetchone()[0]
	# 		return
		

	async def set_setup(self,user_id,st,tf=None,setup_length = None,delete=False):
		async with self._conn_async.cursor() as cursor:
			if delete:
				await cursor.execute("DELETE FROM setups WHERE user_id = %s AND name = %s", (user_id,st))
			elif tf != None and setup_length != None:
				insert_query = "INSERT INTO setups (user_id, name, tf, setup_length) VALUES (%s, %s, %s, %s)"
				await cursor.execute(insert_query, (user_id,st,tf,setup_length))
			else:
				raise Exception('missing args')
		await self._conn_async.commit()
		
	def get_setup_length(self,user_id,st):
		with self._conn.cursor(buffered=True) as cursor:
			cursor.execute('SELECT tf,setup_length from setups WHERE user_id = %s AND name = %s',(user_id,st))
			return cursor.fetchall()[0]
		
	
	def get_setup_sample(self,user_id,st):
		with self._conn.cursor(buffered=True) as cursor:
			cursor.execute('SELECT setup_id, tf,setup_length from setups WHERE user_id = %s AND name = %s',(user_id,st))
			setup_id, tf,setup_length = cursor.fetchall()[0]
			cursor.execute('SELECT * from setup_data WHERE setup_id = %s',(setup_id,))
			values = [[ticker,dt,val] for setup_id,ticker,dt,val in cursor.fetchall()]
			return values, tf,setup_length
		
	
		
	def set_setup_sample(self,user_id,st,data):##################################### ix this shit bruhhg dododosoosdodsfdsiho
		with self._conn.cursor(buffered=True) as cursor:
			cursor.execute('SELECT setup_id from setups WHERE user_id = %s AND name = %s',(user_id,st))
			setup_id = cursor.fetchone()[0]
			query = [[setup_id,ticker,dt,classification] for ticker,dt,classification in data]
			cursor.executemany("INSERT IGNORE INTO setup_data VALUES (%s, %s, %s,%s)", query)
			
		self._conn.commit()
		



	# def alter_table(self):
	# 	with self._conn.cursor(buffered=True) as cursor:
	# 		# SQL command to delete the 'model' column
	# 		delete_column_query = "ALTER TABLE setups DROP COLUMN model;"
	# 		cursor.execute(delete_column_query)

	# 		# SQL command to add the 'setup_length' column
	# 		add_column_query = "ALTER TABLE setups ADD COLUMN setup_length INT;"
	# 		cursor.execute(add_column_query)

	# 		# Commit the changes
	# 		self._conn.commit()

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
			CREATE TABLE setups(
				user_id INT NOT NULL,
				name VARCHAR(255) NOT NULL,
				setup_id INT AUTO_INCREMENT UNIQUE,
				tf VARCHAR(3) NOT NULL,
				setup_length INT NOT NULL,
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
	
#start = datetime.datetime.now()

data = Data()


#if __name__ == '__main__':
	#data.setup()
#asyncio.run(data.init_async_conn())
#data.init_async_conn()

#await data.get_user()
#print(datetime.datetime.now() - start,flush=True)