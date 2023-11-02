import mysql.connector
import os
import pandas as pd
from multiprocessing import Pool
from tqdm import tqdm
import numpy as np
from decimal import Decimal
import datetime

import aiomysql

class Database:
	

	@classmethod
    async def init_pool(cls):
        if cls._pool is None:
            cls._pool = await aiomysql.create_pool(host='localhost', port=3306,
                                                   user='username', password='password',
                                                   db='database_name', charset='utf8mb4',
                                                   cursorclass=aiomysql.DictCursor,
                                                   autocommit=True)
	
	#def __init__
	#def get_df
	#def get_ticker_list
	#def get_setups
	#def add_setup
	#def update
		
	def __init__(self):
		
		def connect():
			db = mysql.connector.connect(host="localhost",user="root",passwd="7+WCy76_2$%g",database='Broker',autocommit=True)  # Enable autocommit
			return db 
		try:  self.db = connect()
		except:
			command = '''
			DROP TABLE IF EXISTS users;
			DROP TABLE IF EXISTS setups;
			DROP TABLE IF EXISTS setup_data;
			DROP TABLE IF EXISTS dfs;
			CREATE TABLE adfs(
				ticker VARCHAR(5) NOT NULL,
				tf VARCHAR(3) NOT NULL,
				dt DATETIME NOT NULL,
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
			'''
			self.c.execute(command)
			self.db = connect()
		self.c = self.db.cursor()
	
	def get_ticker_list(type = 'full'):
		if type == 'full':
			folder = 'C:/dev/Broker/backend/scripts/d/'
			dir_list = os.listdir(folder)
			if len(dir_list) < 10:
				raise Exception('dont have data')
			return [d[:-8] for d in dir_list]
		elif type == 'current':
	
	def legacy_worker(bar):
		ticker, tf, path = bar
		df = pd.read_feather(path)
		df['datetime'] = df['datetime'].astype(str)
		df = df.values.tolist()
		rows = [[ticker, tf] + list(row) for row in df]
		try:
			db = mysql.connector.connect(host="localhost",user="root",passwd="7+WCy76_2$%g",database='Broker',autocommit=True)
			c = db.cursor()
			insert_query = "INSERT IGNORE INTO dfs VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
			c.executemany(insert_query, rows)
			c.close()
			db.close()
		except mysql.connector.Error as err:
			print('something failed')

	def load_legacy_data(self):
		if input('reset db? y/n') == 'y':
			try:self.c.execute("TRUNCATE TABLE dfs")
			except:pass
			for tf in ('d','1min'):
				args = [[ticker, tf, 'C:/dev/broker/backend/scripts/' + tf + '/' + ticker + '.feather'] for ticker in self.get_ticker_list()]
				with Pool(5) as pool:
					list(tqdm(pool.imap_unordered(self.legacy_worker, args), total=len(args)))

	def update(self):
		from Study import Screener as screener
		df = pd.DataFrame({'ticker':Database.get_ticker_list('current')})
		df['tf'] = 'd'
		df['dt'] = None
		ds = Dataset(df)
		ds.update()
		df['tf'] = '1min'
		ds = Dataset(df)
		ds.update()
		ident =  Main.get_config("Data identity")
		if ident == 'desktop':
			weekday = datetime.datetime.now().weekday()
			if weekday == 4:
				Data.backup()
				use = .08
				epochs = 200
				for st in Main.get_setups_list():
					df = Main.sample(st, use)
					sample = Dataset(df)
					sample.load_np('ml',80)
					sample.train(st,use,epochs) 
		Main.refill_backtest()






	

	def get_df(ticker, tf='1d',dt=None,bars=0,offset=0):
		if dt != None:
			query = "SELECT * FROM dfs WHERE ticker = %s AND tf = %s AND dt = %s"
			self.c.execute(query, (ticker, tf,dt))
		else: 
			query = "SELECT * FROM dfs WHERE ticker = %s AND tf = %s"
			self.c.execute(query, (ticker, tf))
		data = self.c.fetchall()
		data = np.array(data, dtype=float)
		if data:
			
			# columns = ['ticker', 'timeframe', 'datetime', 'open', 'high', 'low', 'close', 'volume']
			# df = pd.DataFrame(data, columns=columns)
			# df['datetime'] = pd.to_datetime(df['datetime'])
			# cols = ['datetime'] + [col for col in df if col != 'datetime']
			# df = df[cols]
			# df = df.drop(columns=['ticker', 'timeframe'])
			# df.set_index('datetime',inplace = True)
			# df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].applymap(float)
			return df
		else:
			return None#pd.DataFrame()

	def print_all(self, name, ticker=None):
		try:
			if ticker:
				query = f"SELECT * FROM {name} WHERE ticker = %s"
				self.c.execute(query, (ticker,))
			else:
				query = f"SELECT * FROM {name}"
				self.c.execute(query)
			df = self.c.fetchall()
			if df:
				print(df)
			else:
				print("No data found.")
		except mysql.connector.Error as err:
			print("Error:", err)

if __name__ == '__main__':
	db = Data()
	db.install()
	db.print_all('dfs', 'A')
	data_df = db.get_data('A')
	print(data_df)
	






