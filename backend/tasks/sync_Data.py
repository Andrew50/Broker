from token import EXACT_TOKEN_TYPES
import numpy as np
import  pandas as pd, numpy as np, datetime, mysql.connector, pytz, redis, pickle,  multiprocessing
import numpy as np
import  pandas as pd, os, numpy as np, time,datetime, mysql.connector, pytz, redis, pickle,  multiprocessing, json
from tqdm import tqdm
from collections import defaultdict
import yfinance as yf
import asyncio
from mysql.connector import errorcode

import multiprocessing
import redis
import mysql.connector
from contextlib import closing



class Data:
	


	#eng_project
	def __init__(self):
		#try:
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
		# except:
		# 	self._conn = mysql.connector.connect(host='localhost',port='3307',user='root',password='7+WCy76_2$%g')
		# 	self.setup()












			
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
	
		
	
	def get_ds(self,form = 'match',request='full',tf='1d', bars=0):
		returns = []
		
		if request == 'full':
			if form == 'screener':
				hash_data = self.r.hgetall(tf+form)
				#return {field.decode(): pickle.loads(value) for field, value in hash_data.items()}
				tickers = []
				for ticker, value in hash_data.items():
					try:
						ticker = ticker.decode()
						value = pickle.loads(value)
						if bars:
							padding = bars - value.shape[0]
							if padding > 0:
								pad_width = [(0, padding)] + [(0, 0)] * (value.ndim - 1)  # Pad only the first dimension
								value = np.pad(value, pad_width, mode='constant', constant_values=0)
							value = value[-bars:,:]
						for ii in (2,3,4):
							value[-1,ii] = value[-1,1]
						returns.append(value)
						tickers.append(ticker)
					except TimeoutError: 
						pass
					


				#val = np.array([field.decode() for field, value in hash_data.items()])
				
				return np.array(returns), tickers
			elif form == 'match':
				hash_data = self.r.hgetall(tf+form)
				#return {field.decode(): pickle.loads(value) for field, value in hash_data.items()}
				return [[field.decode(), pickle.loads(value)] for field, value in hash_data.items()]
			

		else:
			


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
		
	def get_finished_study_tickers(self,user_id,st):
		with self._conn.cursor(buffered = True) as cursor:
			query = "SELECT DISTINCT ticker FROM study WHERE user_id = %s AND st = %s"
			cursor.execute(query, (user_id, st))

			return [row[0] for row in cursor.fetchall()]

	def get_study_length(self,user_id,st):
		with self._conn.cursor(buffered = True) as cursor:
			query = "SELECT COUNT(*) FROM study WHERE user_id = %s AND st = %s AND annotation <> ''"
			cursor.execute(query, (user_id, st))
			count = cursor.fetchone()[0]
		return count
			
	def set_study(self,user_id,st,instances):
		with self._conn.cursor(buffered = True) as cursor:
			query = [[user_id,st,ticker,dt,''] for ticker,tf,dt in instances]
			cursor.executemany("INSERT INTO study VALUES (%s, %s, %s, %s, %s)",query)
		self._conn.commit()

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


	
		



data = Data()
