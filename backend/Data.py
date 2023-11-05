
from turtle import update
import numpy as np
import array, os, pandas as pd, numpy as np, datetime, mysql.connector, pytz
from tqdm import tqdm
import yfinance as yf

class Database:
	
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


	def get_model(self,user_id,st):
		with self._conn.cursor(buffered=True) as cursor:
			cursor.execute('SELECT model from setups WHERE user_id = %s AND name = %s',(user_id,st))
			return cursor.fetchone()[0]

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
		
	def set_sample(self,user_id,st,ticker,dt):
		with self._conn.cursor(buffered=True) as cursor:
			
			cursor.execute('SELECT setup_id from setups WHERE user_id = %s AND name = %s',(user_id,st))
			setup_id = cursor.fetchone()[0]
			cursor.execute("INSERT IGNORE INTO setup_data VALUES (%s, %s, %s)", (setup_id,ticker,dt))
			
		self._conn.commit()
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
	
	def get_df(self, ticker, tf='1d', dt=None, bars=0, pm=True):
		cursor = self._conn.cursor(buffered=True)
		if dt != None:
			query = "SELECT dt, open, high, low, close, volume FROM dfs WHERE ticker = %s AND tf = %s AND dt <= %s ORDER BY dt ASC"
			cursor.execute(query, (ticker, tf, dt))
		else:
			query = "SELECT dt, open, high, low, close, volume FROM dfs WHERE ticker = %s AND tf = %s ORDER BY dt ASC"
			cursor.execute(query, (ticker, tf))
			
		data = cursor.fetchall()

		
		return data
	
	def update(self,force_retrain=False):

		with self._conn.cursor(buffered=True) as cursor:
			
			#update full ticker list
			
			# current_ticker_list = self.get_ticker_list('current')
			# for ticker in current_ticker_list:
			# 	cursor.executemany('INSERT IGNORE INTO full_ticker_list VALUES (%s)',(ticker,))
		
			# self._conn.commit()

			#update data


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
					
					except TimeoutError:
						pass
					
			

			#update models
			# if datetime.datetime.now().day == 4 or force_retrain:
				
			# 	cursor.execute('SELECT * from setups')
			# 	setups = cursor.fetchall()
			# 	for setup_id, st, tf, model in setups:
			# 		cursor.execute('SELECT * from')











			#backup
	
	
	def __init__(self):
		try:
			dbconfig = {"host": "localhost","port": 3306,"user": "root","password": "7+WCy76_2$%g","database": 'broker'}
			self._conn = mysql.connector.connect(**dbconfig)
			with self._conn.cursor(buffered=True) as cursor:
				cursor.execute("SELECT COUNT(*) FROM dfs;")
				count = cursor.fetchall()[0][0]
				assert count > 0
				if count < 8000*300:
					print(f'WARNING: DATA ISNT COMPLETE! ONLY {count} DAILY DATAPOINTS!')
			
		except:
			dbconfig = {
				"host": "localhost",
				"port": 3306,
				"user": "root",
				"password": "7+WCy76_2$%g",#TODO
			}
			self._conn = mysql.connector.connect(**dbconfig)
			
			# try:
			# 	cursor.execute("USE broker;")
			# 	self._conn.commit()
				
				
			# except Exception as e:
			# 	print(e)
			self.load_from_legacy()

	def close_connection(self):
		self._conn.close()
		
	

	def load_from_legacy(self):
		with self._conn.cursor(buffered=True) as cursor:
			##configure tables
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
    open DECIMAL(10, 4),
    high DECIMAL(10, 4),
    low DECIMAL(10, 4),
    close DECIMAL(10, 4),
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
    UNIQUE(ticker, dt),
    FOREIGN KEY (setup_id) REFERENCES setups(setup_id)
);
CREATE INDEX id_index ON setup_data (setup_id);
CREATE TABLE full_ticker_list(ticker VARCHAR(5) NOT NULL);
CREATE TABLE current_ticker_list(ticker VARCHAR(5) NOT NULL);
			"""
			commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
			for command in commands:cursor.execute(command)
			##transfer full_ticker_list
			df = pd.read_feather("C:/dev/Broker/backend/sync/files/full_scan.feather")
			df = df['ticker'].tolist()
			df = [[x] for x in df]
			insert_query = "INSERT INTO full_ticker_list VALUES (%s)"
			cursor.executemany(insert_query, df)
			self._conn.commit()
			##transfer data from backend/d/
			if True:
				
				for tf in ['1d']:
					args = [[ticker, tf, 'C:/dev/broker/backend/' + tf + '/' + ticker + '.feather'] for ticker in self.get_ticker_list()]
					for ticker, tf, path in tqdm(args,desc='Transfering Dataframes'):
						try:
							df = pd.read_feather(path)
							df['datetime']= (df['datetime'].astype(np.int64) // 10**9)
							df = df.values.tolist()
							rows = [[ticker, tf] + row for row in df]
							insert_query = "INSERT IGNORE INTO dfs VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
							cursor.executemany(insert_query, rows)
							self._conn.commit()
						except : #if d doesnt exist or theres no data then this gets hit every loop
							pass
		self.update()


	
	def is_market_open(self=None):  # Change to a boolean at some point
		if (datetime.datetime.now().weekday() >= 5):
			return False  # If saturday or sunday
		dt = datetime.datetime.now(pytz.timezone('US/Eastern'))
		hour = dt.hour
		minute = dt.minute
		if hour >= 10 and hour <= 16:
			return True
		elif hour == 9 and minute >= 30:
			return True
		return False

	def print_all(self):
		query = "SELECT * FROM dfs"
		cursor = self._conn.cursor(buffered=True)
		cursor.execute(query)
		data = cursor.fetchall()
		print(data)
	
	def format_datetime(dt,reverse=False):
		if type(dt) == int:
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
		return dt
		if not reverse:
			dt = dt.timestamp()
		else:
			dt = datetime.datetime.fromtimestamp(dt)
		return dt

class Dataset:
	
	def __init__(self, db, request='full',tf='d', bars=0, value=None, pm=True):
		if request == 'full':
			request = [[ticker,None] for ticker in db.get_ticker_list('full')]
		self.dfs = [Data(db,ticker, tf, dt, bars, value, pm) for ticker,dt in request]
		self.bars = bars
		self.len = len(self.dfs)
		

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
			print(f'{st} cannot be trained with only {ones} positives')
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

class Data:

	def __init__(self, db, ticker='QQQ', tf='d', dt=None, bars=0,value=None, pm=True):
		# try:
		self.df = db.get_df(ticker,tf,dt,bars,pm)
		# except:
		# 	self.df = []
		self.len = len(self.df)
		self.ticker = ticker
		self.tf = tf
		self.dt = dt
		self.value = value

	def load_score(self, st, model=None):
		if model == None:
			model = Main.load_model(st)
		returns = []
		for df, index in self.np:
			score = model.predict(df)
			returns.append([self.ticker, self.df.index[index], st, score])
		self.score = returns
		return returns

if __name__ == '__main__':
	db = Database()
	#db.update()
	# db.set_user(email = 'billingsandrewjohn@gmail.com',password = 'password')
	# # except:
	# # 	pass
	# # #except: pass
	# user_id = db.get_user('billingsandrewjohn@gmail.com','password')
	# db.set_setup(user_id,'EP','1d')
	# db.set_sample(user_id,'EP','AAPL',10)
	# print(db.get_sample(user_id,'EP'))
	# #db.set_user(user_id,delete=True)
	# ##print(settings)

	
