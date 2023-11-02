import array
import os
import pandas as pd
import numpy as np
import asyncio
import datetime
import aiomysql

class Database:
	_pool = None

	def __init__(self):
		if self._pool == None:
			self.init_pool()

	@classmethod
	async def init_pool(cls):
		if cls._pool is None:
			dbconfig = {
				"host": "localhost",
				"port": 3306,
				"user": "root",
				"password": "7+WCy76_2$%g",
				"db": 'Broker',
				"autocommit": True
			}
			cls._pool = await aiomysql.create_pool(**dbconfig)

	@classmethod
	async def close_pool(cls):
		cls._pool.close()
		await cls._pool.wait_closed()
		
	async def get_ticker_list(self,type='full'):
		async with self._pool.acquire() as conn:
			async with conn.cursor(aiomysql.DictCursor) as cur:
				if type == 'full':
					query = "SELECT * FROM full_ticker_list"
					await cur.execute(query)
					data = await cur.fetchall()
					return data
				

	class Database:
	# ... [other class methods]
		if input('reset db? y/n') == 'y':
	
			async def load_from_legacy(self):
				# SQL statements as a multiline string
				sql_commands = """
				DROP TABLE IF EXISTS users;
				DROP TABLE IF EXISTS setups;
				DROP TABLE IF EXISTS setup_data;
				DROP TABLE IF EXISTS dfs;
				CREATE TABLE dfs(
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
				CREATE TABLE full_ticker_list(
					ticker VARCHAR(5) NOT NULL
				);
				"""
		
				# Split the SQL commands by semicolon and remove any empty lines
				commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
		
				async with self._pool.acquire() as conn:
					async with conn.cursor(aiomysql.DictCursor) as cur:
						# Execute each SQL command
						for command in commands:
							await cur.execute(command)
				try: await cur.execute("TRUNCATE TABLE dfs")
				except:pass
				for tf in ('d','1min'):
					args = [[ticker, tf, 'C:/dev/broker/backend/scripts/' + tf + '/' + ticker + '.feather'] for ticker in self.get_ticker_list()]
					with Pool(5) as pool:
						list(tqdm(pool.imap_unordered(self.legacy_worker, args), total=len(args)))
						# Once you have created the tables, if you wish to insert data, you can use:
						# insert_query = "INSERT IGNORE INTO full_ticker_list VALUES (%s)"
						# await cur.executemany(insert_query, ticker)


	async def legacy_worker(self, bar):
		ticker, tf, path = bar
		df = pd.read_feather(path)
		df['datetime'] = df['datetime'].astype(str)
		df = df.values.tolist()
		rows = [[ticker, tf] + list(row) for row in df]
		
		async with self._pool.acquire() as conn:
			async with conn.cursor(aiomysql.DictCursor) as cur:
				insert_query = "INSERT IGNORE INTO dfs VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
				await cur.executemany(insert_query, rows)
				

	async def get_df(self, ticker, tf='d', dt=None, bars=0, offset=0):
		async with self._pool.acquire() as conn:
			async with conn.cursor(aiomysql.DictCursor) as cur:
				if dt:
					query = "SELECT * FROM dfs WHERE ticker = %s AND tf = %s AND dt = %s"
					await cur.execute(query, (ticker, tf, dt))
				else:
					query = "SELECT * FROM dfs WHERE ticker = %s AND tf = %s"
					await cur.execute(query, (ticker, tf))
				
				data = await cur.fetchall()
				array_data = [(entry['dt'], float(entry['open']), float(entry['high']), float(entry['low']), float(entry['close']), entry['volume']) for entry in data]
				np_array = np.array(array_data, dtype=[('dt', 'O'), ('open', 'f8'), ('high', 'f8'), ('low', 'f8'), ('close', 'f8'), ('volume', 'f8')])
				return array_data

async def main():
	await Database.init_pool()
	db = Database()
	ticker_list = await db.get_ticker_list('full')
	start = datetime.datetime.now()
	
	for ticker in ticker_list:
		result = await db.get_df('AAPL')
	print(result)
	print(datetime.datetime.now() - start)
	await Database.close_pool()

if __name__ == '__main__':
	asyncio.run(main())
