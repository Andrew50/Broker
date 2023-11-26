import aiomysql, aioredis, pickle, datetime, pytz

class Data:
	
	async def init_async_conn(self):
		# self.redis_pool = await aioredis.create_redis_pool(
		# 	f'redis://redis', minsize=1, maxsize=20)
		self.redis_pool = aioredis.Redis(host='redis', port=6379)
		self.mysql_pool = await aiomysql.create_pool(
			host='mysql', port=3306, user='root', password='7+WCy76_2$%g', 
			db='broker', minsize=1, maxsize=20)

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

	async def get_df(self, form='chart', ticker='QQQ', tf='1d', dt=None, bars=0, pm=True):
		#async with self.redis_pool.get() as conn:
			
		data = await self.redis_pool.hget(tf+form,ticker)
		if not form == 'chart': data = pickle.loads(data)
		if dt:
			index = Data.findex(data,dt)
			data = data[:index+1]
		if bars:
			data = data[-bars:]
		if not pm:
			raise Exception('to code')
		return data

	async def get_user(self, email, password):
		async with self.mysql_pool.acquire() as conn:
			async with conn.cursor() as cursor:
				await cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
				user_data = await cursor.fetchone()
				if user_data and len(user_data) > 0:
					if password == user_data[2]:  # Assuming password is at index 2
						return user_data[0]   
	
	async def set_user(self, user_id=None, email=None, password=None, settings_string=None, delete=False):
		async with self.mysql_pool.acquire() as conn:
			async with conn.cursor() as cursor:
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
			await conn.commit()
				
	async def get_settings(self,user_id):
		async with self.mysql_pool.acquire() as conn:
			async with conn.cursor() as cursor:
				await cursor.execute("SELECT settings FROM users WHERE id = %s", (user_id,))
				settings = await cursor.fetchone()
				return settings[0]
		
	async def get_user_setups(self,user_id):
		async with self.mysql_pool.acquire() as conn:
			async with conn.cursor() as cursor:
				await cursor.execute("SELECT name, tf, setup_length from setups WHERE user_id = %s",(user_id,))
				return await cursor.fetchall()

	async def set_setup(self,user_id,st,tf=None,setup_length = None,delete=False):
		async with self.mysql_pool.acquire() as conn:
			async with conn.cursor() as cursor:
				if delete:
					await cursor.execute("DELETE FROM setups WHERE user_id = %s AND name = %s", (user_id,st))
				elif tf != None and setup_length != None:
					insert_query = "INSERT INTO setups (user_id, name, tf, setup_length) VALUES (%s, %s, %s, %s)"
					await cursor.execute(insert_query, (user_id,st,tf,setup_length))
				else:
					raise Exception('missing args')
			await conn.commit()