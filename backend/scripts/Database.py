import array, os, pandas as pd, numpy as np, datetime, mysql.connector

class Database:
	
#get model
#get sample
#set sample
#set settings
#auth

	def close_pool(self):
		self._conn.close()

	def get_ticker_list(self, type='full'):
		cursor = self._conn.cursor(dictionary=True)
		if type == 'full':
			query = "SELECT * FROM full_ticker_list"
			cursor.execute(query)
			data = cursor.fetchall()
			cursor.close()
			return data

	def get_df(self, ticker, tf='d', dt=None, bars=0, offset=0):
		cursor = self._conn.cursor(dictionary=True)
		if dt:
			query = "SELECT * FROM dfs WHERE ticker = %s AND tf = %s AND dt = %s"
			cursor.execute(query, (ticker, tf, dt))
		else:
			query = "SELECT * FROM dfs WHERE ticker = %s AND tf = %s"
			cursor.execute(query, (ticker, tf))
		data = cursor.fetchall()
		data = np.array([[str(entry['dt']), float(entry['open']), float(entry['high']), float(entry['low']), float(entry['close']), float(entry['volume'])] for entry in data])
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
		
		commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
		cursor = self._conn.cursor()
		for command in commands:
			cursor.execute(command)
		try: cursor.execute("TRUNCATE TABLE dfs")
		except:pass
		for tf in ('d','1min'):
			args = [[ticker, tf, 'C:/dev/broker/backend/scripts/' + tf + '/' + ticker + '.feather'] for ticker in self.get_ticker_list()]
			for ticker, tf, path in args:
				df = pd.read_feather(path)
				df['datetime'] = df['datetime'].astype(str)
				df = df.values.tolist()
				rows = [[ticker, tf] + list(row) for row in df]
		
				cursor = self._conn.cursor()
				insert_query = "INSERT IGNORE INTO dfs VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
				cursor.executemany(insert_query, rows)
				self._conn.commit()
				cursor.close()

if __name__ == '__main__':
	db = Database()
	ticker_list = db.get_ticker_list('full')
	df = db.get_df('AAPL')
	print(df)
	db.close_pool()

