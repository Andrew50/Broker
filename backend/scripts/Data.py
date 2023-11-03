
import numpy as np
import array, os, pandas as pd, numpy as np, datetime, mysql.connector
from tqdm import tqdm



class Database:
	
#get model
#get sample
#set sample
#set settings
#auth

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
		
		ticker = self.ticker
		
		tf = self.tf
		path = self.path
		exists = True
		try:
			df = self.df
			last_day = self.df.index[-1] 
		except: exists = False
		print(tf)
		if tf == '1d' or tf == 'd':
			ytf = '1d'
			period = '25y'
		elif tf == '1min':
			ytf = '1m'
			period = '5d'
		ydf = yf.download(tickers = ticker, period = period, group_by='ticker', interval = ytf, ignore_tz = True, progress=False, show_errors = False, threads = False, prepost = True) 
		ydf.drop(axis=1, labels="Adj Close",inplace = True)
		ydf.rename(columns={'Open':'open','High':'high','Low':'low','Close':'close','Volume':'volume'}, inplace = True)
		ydf.dropna(inplace = True)
		if Main.is_market_open() == 1: ydf.drop(ydf.tail(1).index,inplace=True)
		if not exists: df = ydf
		else:
			try: index = Data.findex(ydf, last_day) 
			except: return
			ydf = ydf[index + 1:]
			df = pd.concat([df, ydf])
		df.index.rename('datetime', inplace = True)
		if not df.empty: 
			if tf == '1min': pass
			elif tf == 'd': df.index = df.index.normalize() + pd.Timedelta(minutes = 570)
			df = df.reset_index()
			feather.write_feather(df,path)
		pass
		#update full_ticker_list
		#update data
		#retrain
		#calc account
		#backup
	
	def __init__(self):
		dbconfig = {
			"host": "localhost",
			"port": 3306,
			"user": "root",
			"password": "7+WCy76_2$%g",#TODO
			"database": 'Broker',
			"autocommit": True
		}
		self._conn = mysql.connector.connect(**dbconfig)

	def close_pool(self):
		self._conn.close()
	
	def format_datetime(dt,reverse=False):
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
		sql_commands = """
		DROP TABLE IF EXISTS users;
		DROP TABLE IF EXISTS setups;
		DROP TABLE IF EXISTS setup_data;
		DROP TABLE IF EXISTS dfs;
		DROP TABLE IF EXISTS full_ticker_list;
		CREATE TABLE dfs(
			ticker VARCHAR(5) NOT NULL,
			tf VARCHAR(3) NOT NULL,
			dt BIGINT NOT NULL,
			open DECIMAL(10, 4),
			high DECIMAL(10, 4),
			low DECIMAL(10, 4),
			close DECIMAL(10, 4),
			volume FLOAT,
			PRIMARY KEY (ticker, tf, dt)
		);
		CREATE TABLE setup_data(
			id INT NOT NULL,
			ticker VARCHAR(5) NOT NULL,
			dt INT NOT NULL
		);
		CREATE INDEX id_index ON setup_data (id);
		CREATE TABLE setups(
			id INT NOT NULL,
			setup_id INT NOT NULL,
			name VARCHAR(255) NOT NULL,
			tf VARCHAR(3) NOT NULL,
			FOREIGN KEY (setup_id) REFERENCES setup_data(id)
		);
		CREATE INDEX id_index ON setups (id);
		CREATE TABLE users(
			id INT PRIMARY KEY,
			setups_id INT NOT NULL,
			email VARCHAR(255),
			password VARCHAR(255),
			settings TEXT,
			FOREIGN KEY (setups_id) REFERENCES setups(id)
		);
		CREATE TABLE full_ticker_list(
			ticker VARCHAR(5) NOT NULL
		);
		"""
		
		create_database_command = "CREATE DATABASE IF NOT EXISTS broker;"
		
		commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
		cursor = self._conn.cursor()
		cursor.execute(create_database_command)
		for command in commands:
			cursor.execute(command)
		#try: cursor.execute("TRUNCATE TABLE dfs")
		#except:pass
		#for tf in ('d','1min'):
		df = pd.read_feather("C:/dev/Broker/backend/scripts/sync/files/full_scan.feather")
		df = df['ticker'].tolist()
		df = [[x] for x in df]
		insert_query = "INSERT INTO full_ticker_list VALUES (%s)"
		cursor = self._conn.cursor()
		cursor.executemany(insert_query, df)
		self._conn.commit()
		for tf in ('d'):
			args = [[ticker, tf, 'C:/dev/broker/backend/scripts/' + tf + '/' + ticker + '.feather'] for ticker in self.get_ticker_list()]
			
			for ticker, tf, path in tqdm(args,desc='Transfering Dataframes'):
				try:
					df = pd.read_feather(path)
					df = df.values.tolist()
					rows = [[ticker, tf,Database.format_datetime(row[0])] + list(row)[1:] for row in df]
					insert_query = "INSERT INTO dfs VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
					cursor.executemany(insert_query, rows)
					self._conn.commit()
				except:
					pass
		cursor.close()


class Dataset: #object
	

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

	def init_worker(pack):
		bar, other = pack
		ticker = bar['ticker']
		dt = bar['dt']
		tf = bar['tf']
		bars, offset, value, pm, np_bars = other
		# needs to be fixed becaujse m
		return Data(ticker, tf, dt, bars, offset, value, pm, np_bars)

	def __init__(self, request='full',tf='d', bars=0, offset=0, value=None, pm=True):
		
		if request == 'full':
			request = [[ticker,None] for ticker in db.get_ticker_list('full')]
		for ticker, dt in request:
			self.dfs = Data(ticker, tf, dt, bars, offset, value, pm)
		self.bars = bars
		self.offset = offset
		self.len = len(self.dfs)
		
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

	def findex(self, dt):
		dt = Main.format_date(dt)
		if not isinstance(self, pd.DataFrame):
			df = self.df
		else:
			df = self
		i = int(len(df)/2)		
		k = int(i/2)
		while k != 0:
			date = df.index[i].to_pydatetime()
			if date > dt:
				i -= k
			elif date < dt:
				i += k
			k = int(k/2)
		while df.index[i].to_pydatetime() < dt:
			i += 1
		while df.index[i].to_pydatetime() > dt:
			i -= 1
		return i