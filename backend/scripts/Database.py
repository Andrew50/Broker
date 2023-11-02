import os
import pandas as pd
from multiprocessing import Pool
from tqdm import tqdm
import numpy as np
from decimal import Decimal
import datetime
import asyncio
import mysql.connector
from mysql.connector import pooling

class Database:

	_pool = None
	
	@classmethod
	def init_pool(cls):
		if cls._pool is None:
			dbconfig = {"host": "localhost","user": "root","passwd": "7+WCy76_2$%g","database": 'Broker',"autocommit": True}
			cls._pool = mysql.connector.pooling.MySQLConnectionPool(pool_name="mypool", pool_size=5, **dbconfig)
	
	def __init__(self):
		if not Database._pool:
			self.init_pool()
		self.db = self._pool.get_connection()
		self.c = self.db.cursor()

	async def legacy_worker(self, bar):
		ticker, tf, path = bar
		df = pd.read_feather(path)
		df['datetime'] = df['datetime'].astype(str)
		df = df.values.tolist()
		rows = [[ticker, tf] + list(row) for row in df]
		try:
			conn = self._pool.get_connection()
			c = conn.cursor()
			insert_query = "INSERT IGNORE INTO dfs VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
			c.executemany(insert_query, rows)
			c.close()
			conn.close()
		except mysql.connector.Error as err:
			print('something failed')
			
	async def get_cursor(self):
		self.connection = await Database._pool.acquire()
		self.c = await self.connection.cursor()

	async def release_cursor(self):
		await self.c.close()
		Database._pool.release(self.connection)

	async def load_legacy_data(self):
		if input('reset db? y/n') == 'y':
			try:self.c.execute("TRUNCATE TABLE dfs")
			except:pass
			for tf in ('d','1min'):
				args = [[ticker, tf, 'C:/dev/broker/backend/scripts/' + tf + '/' + ticker + '.feather'] for ticker in self.get_ticker_list()]
				with Pool(5) as pool:
					list(tqdm(pool.imap_unordered(self.legacy_worker, args), total=len(args)))

	# async def update(self):
	# 	from Study import Screener as screener
	# 	df = pd.DataFrame({'ticker':Database.get_ticker_list('current')})
	# 	df['tf'] = 'd'
	# 	df['dt'] = None
	# 	ds = Dataset(df)
	# 	ds.update()
	# 	df['tf'] = '1min'
	# 	ds = Dataset(df)
	# 	ds.update()
	# 	ident =  Main.get_config("Data identity")
	# 	if ident == 'desktop':
	# 		weekday = datetime.datetime.now().weekday()
	# 		if weekday == 4:
	# 			Data.backup()
	# 			use = .08
	# 			epochs = 200
	# 			for st in Main.get_setups_list():
	# 				df = Main.sample(st, use)
	# 				sample = Dataset(df)
	# 				sample.load_np('ml',80)
	# 				sample.train(st,use,epochs) 
	# 	Main.refill_backtest()



	def print_all(self, name, ticker=None):
		if ticker:
			query = f"SELECT * FROM {name} WHERE ticker = %s"
			self.c.execute(query, (ticker,))
		else:
			query = f"SELECT * FROM {name}"
			self.c.execute(query)
		df = self.c.fetchall()
		if df:
			print(df)

	async def get_df(self,ticker, tf='1d',dt=None,bars=0,offset=0):
		await self.get_cursor()
		try:
			if dt != None:
				query = "SELECT * FROM dfs WHERE ticker = %s AND tf = %s AND dt = %s"
				await self.c.execute(query, (ticker, tf, dt))
			else: 
				query = "SELECT * FROM dfs WHERE ticker = %s AND tf = %s"
				await self.c.execute(query, (ticker, tf))
			data = await self.c.fetchall()
			data = await np.array(data)
			return data
		except:
			data = None
		finally:
			await self.release_cursor()
			return data

if __name__ == '__main__':
	db = Database()
	result = asyncio.run(db.get_df('TSLA'))
	print(result)



