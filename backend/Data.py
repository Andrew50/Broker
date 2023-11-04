
from turtle import update
import numpy as np
import array, os, pandas as pd, numpy as np, datetime, mysql.connector, pytz
from tqdm import tqdm
import yfinance as yf

class Database:
	
	def is_market_open():  # Change to a boolean at some point
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

	def get_model(user_id,st):
		pass

	def get_sample(self,user_id,st):
		with self._conn.cursor() as cursor:
			query = """
			SELECT sd.*
			FROM setup_data sd
			JOIN setups s ON sd.id = s.id
			JOIN users u ON s.setup_id = u.setups_id
			WHERE u.id = %s AND s.name = %s
			"""
			cursor.execute(query, (user_id, st))
			rows = cursor.fetchall()

		
	def set_sample(self,user_id,st,ticker,tf,dt):
		with self._conn.cursor() as cursor:
			query = """
			SELECT sd.*
			FROM setup_data sd
			JOIN setups s ON sd.id = s.id
			JOIN users u ON s.setup_id = u.setups_id
			WHERE u.id = %s AND s.name = %s
			"""
			cursor.execute(query, (user_id, st))
			rows = cursor.fetchall()
			

			setup_id = cursor.fetchone()


			cursor.execute("INSERT IGNORE INTO setup_data VALUES (%s, %s, %s, %s, %s, %s, %s, %s)", (setup_id,ticker,dt))
			#setup = cursor.fetchone()

	def set_settings(user_id,setting_string):
		pass
	def get_ticker_list(self, type='full'):
		cursor = self._conn.cursor(dictionary=True)
		if type == 'full':
			query = "SELECT * FROM full_ticker_list"
			cursor.execute(query)
			data = cursor.fetchall()
			cursor.close()
			data = [item['ticker'] for item in data]
			return data
		elif type == 'current':
			raise Exception('need current func. has to pull from tv or something god')
	
	def get_df(self, ticker, tf='d', dt=None, bars=0, pm=True):
		print(ticker)
		print(tf)
		print(dt)
		cursor = self._conn.cursor(dictionary=True)
		if dt != None:
			query = "SELECT * FROM dfs WHERE ticker = %s AND tf = %s AND dt = %s"
			cursor.execute(query, (ticker, tf, dt))
		else:
			query = "SELECT * FROM dfs WHERE ticker = %s AND tf = %s"
			cursor.execute(query, (ticker, tf))
		data = cursor.fetchall()
		data = np.array([[float(entry['dt']), float(entry['open']), float(entry['high']), float(entry['low']), float(entry['close']), float(entry['volume'])] for entry in data])
		return data
	
	def update(self):
		#update full ticker list
		#update data
		#update models
		#backup
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
		cursor = self._conn.cursor()
		for ticker in tqdm(ticker_list):
			for tf in ['1d']:
				try:
					df = self.get_df(ticker,tf)
					last_day = df[-1:0]
					
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
					ydf.reset_index(inplace = True)
					if type(last_day) == int:
						index = findex(ydf, last_day) 
						ydf = ydf[index + 1:]
					ydf = ydf.values.tolist()
					ydf = [[ticker, tf] + row for row in ydf]
					insert_query = "INSERT INTO dfs VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
					cursor.executemany(insert_query, ydf)
					self._conn.commit()
					
				except TimeoutError:
					pass
		cursor.close()
		

	
	
	def __init__(self,startup_check=False):
	#def __init__(self,startup_check=False):
		try:
			#if startup_check: raise IndexError
	
			dbconfig = {
				"host": "localhost",
				"port": 3306,
				"user": "root",
				"password": "7+WCy76_2$%g",#TODO
				"database": 'broker',
			}
			self._conn = mysql.connector.connect(**dbconfig)
			cursor.execute("SELECT COUNT(*) FROM dfs;")
			count = cursor.fetchall()
			assert count[0][0] > 5000*300
			
		except:
			dbconfig = {
				"host": "localhost",
				"port": 3306,
				"user": "root",
				"password": "7+WCy76_2$%g",#TODO
			}
			self._conn = mysql.connector.connect(**dbconfig)
			cursor = self._conn.cursor()
			# try:
			# 	cursor.execute("USE broker;")
			# 	self._conn.commit()
				
				
			# except Exception as e:
			# 	print(e)
			self.load_from_legacy()

	def close_connection(self):
		self._conn.close()
		
	def print_all(self):
		query = "SELECT * FROM dfs"
		cursor = self._conn.cursor()
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

	def load_from_legacy(self):
		with self._conn.cursor() as cursor:
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
-- print a table
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
    email VARCHAR(255),
    password VARCHAR(255),
    settings TEXT
);
CREATE TABLE setups(
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    setup_id INT NOT NULL UNIQUE,
    tf VARCHAR(3) NOT NULL,
    model BINARY,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX user_id_index ON setups (user_id);
CREATE INDEX name_index ON setups (name);
CREATE TABLE setup_data(
    setup_id INT NOT NULL,
    ticker VARCHAR(5) NOT NULL,
    dt INT NOT NULL,
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

class Dataset:
	
	def __init__(self, db, request='full',tf='d', bars=0, offset=0, value=None, pm=True):
		
		if request == 'full':
			request = [[ticker,None] for ticker in self.get_ticker_list('full')]
		for ticker, dt in request:
			self.dfs.append(Data(db,ticker, tf, dt, bars, offset, value, pm))
		self.bars = bars
		self.offset = offset
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
		try:
			self.df = db.get_df(ticker,tf,dt,bars,pm)
		except:
			self.df = []
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
	db = Database(True)
