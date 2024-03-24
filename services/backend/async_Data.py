import aiomysql, aioredis, pickle, datetime, pytz, json, uuid

class Data:

    async def init_async_conn(self):
    
        self.cache = aioredis.Redis(host='cache', port=6379)
        self.db = await aiomysql.create_pool(
            host='db', port=3306, user='root', password='7+WCy76_2$%g', 
            db='broker', minsize=1, maxsize=20)
        
    async def queue_task(self,func_ident,args,user_id):
        task_id = str(uuid.uuid4())
        task_data = {'id':task_id,'func':func_ident,'args':args,'user_id':user_id}
        await self.cache.lpush('task_queue_1',json.dumps(task_data))
        #return json.dumps({'task_id':task_id})
        #return task_id
        return json.dumps(task_id)
    
    async def get_task_result(self,task_id):
        return await self.cache.get(f"result:{task_id}")
    
    async def delete_task_result(self,task_id):
        await self.cache.delete(f"result:{task_id}")
    
    async def get_trainer_queue(self,user_id,st):
        return await self.cache.rpop(str(user_id)+st)
    
    async def get_trainer_queue_size(self, user_id, st):
        # Use await with aioredis operations
        return await self.cache.llen(str(user_id) + st)

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
    
    async def get_current_price(self,ticker):
        val = await self.cache.hget('current_price',ticker)
        return pickle.loads(val)

    async def get_df(self, form='chart', ticker='QQQ', tf='1d', dt=None, bars=0, pm=True):
        #async with self.cache.get() as conn:
        data = await self.cache.hget(tf+'_'+form,ticker)
        return data
        
        if form == 'chart': 
            
            if dt:
                normal_data = await self.cache.hget(tf+'screener',ticker)
                normal_data = pickle.loads(normal_data)
                index = Data.findex(normal_data,dt) + 1 #add 1 becuase screener format len is 1 less then chart len
                data = json.loads(data)
                data = data[:index+1] 
                data = json.dumps(data)
            if bars:
                raise Exception("to code")
            if not pm:
                raise Exception('to code')
        else:
            raise Exception('to code')
        return data
    

    @staticmethod
    async def is_market_open(pm=False):
        dt = datetime.datetime.now(pytz.timezone('US/Eastern'))
        if dt.weekday() >= 5:
            return False
        hour = dt.hour
        minute = dt.minute
        if pm:
            if hour >= 16 or hour < 4:
                return False
            return True
        else:
            if hour >= 10 and hour <= 16:
                return True
            elif hour == 9 and minute >= 30:
                return True
            return False

    #eng_project
    async def get_user(self, username, password):
        async with self.db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
                user_data = await cursor.fetchone()
                if user_data and len(user_data) > 0:
                    if password == user_data[2]:  # Assuming password is at index 2
                        return user_data[0]   
    #eng_project
    async def set_user(self, user_id=None, username=None, password=None, settings_string=None, delete=False):
        async with self.db.acquire() as conn:
            async with conn.cursor() as cursor:
                if user_id is not None:
                    if not delete:
                        fields = []
                        values = []
                        if username is not None:
                            fields.append("username = %s")
                            values.append(username)
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
                    insert_query = "INSERT INTO users (username, password, settings) VALUES (%s, %s, %s)"
                    await cursor.execute(insert_query, (username, password, settings_string if settings_string is not None else ''))
            await conn.commit()
            
    async def get_watchlists(self,user_id):
        async with self.db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT name, ticker FROM watchlists WHERE user_id = %s", (user_id,))
                list_of_lists = await cursor.fetchall()
                if list_of_lists == None:
                    return {}
                name_to_tickers = {}
                for name, ticker in list_of_lists:
                    if name in name_to_tickers:
                        name_to_tickers[name].append([ticker])
                    else:
                        name_to_tickers[name] = [[ticker]]

                return name_to_tickers
            
    async def set_watchlist(self,user_id,ticker,watchlist_name,delete):
        async with self.db.acquire() as conn:
            async with conn.cursor() as cursor:
                if delete:
                    query = ("DELETE FROM watchlists WHERE user_id = %s and name = %s and ticker = %s")
                else:
                    query = ("INSERT INTO watchlists (user_id, name, ticker) VALUES (%s, %s, %s)")
                    
                await cursor.execute(query,(user_id,watchlist_name,ticker))
                await conn.commit()
            
    async def set_annotation(self,user_id,st,ticker,tf,dt,annotation):
        async with self.db.acquire() as conn:
            async with conn.cursor() as cursor:
                if annotation != '' and annotation != None:
                    query = "UPDATE study SET annotation = %s WHERE user_id = %s AND st = %s AND ticker = %s AND dt = %s"
                    await cursor.execute(query, (annotation, user_id, st, ticker, dt))
                    await conn.commit()
                await cursor.execute("SELECT ticker,dt FROM study where user_id = %s and st = %s and annotation = ''",(user_id,st))
                ticker,dt = (await cursor.fetchone())[0]
                instance = [ticker,tf,dt]
            return instance

    async def get_study(self,user_id,st):
        async with self.db.acquire() as conn:
            async with conn.cursor() as cursor:
                pass

                         
    async def get_settings(self,user_id):
        async with self.db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT settings FROM users WHERE id = %s", (user_id,))
                settings = await cursor.fetchone()
                return settings[0]
        
    async def get_user_setups(self,user_id):
        async with self.db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("SELECT name, tf, setup_length, sample_size, score from setups WHERE user_id = %s",(user_id,)) #todo add reqs
                return await cursor.fetchall()

    async def set_setup(self,user_id,st,tf=None,setup_length = None,delete=False):
        async with self.db.acquire() as conn:
            async with conn.cursor() as cursor:
                if delete:
                    await cursor.execute("DELETE FROM setups WHERE user_id = %s AND name = %s", (user_id,st))
                elif tf != None and setup_length != None:
                    insert_query = "INSERT INTO setups (user_id, name, tf, setup_length) VALUES (%s, %s, %s, %s)"
                    await cursor.execute(insert_query, (user_id,st,tf,setup_length))
                else:
                    raise Exception('missing args')
            await conn.commit()

    async def set_single_setup_sample(self,user_id,st,ticker,dt,value):##################################### ix this shit bruhhg dododosoosdodsfdsiho
        async with self.db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute('SELECT setup_id from setups WHERE user_id = %s AND name = %s',(user_id,st))
                setup_id = (await cursor.fetchone())[0]
                await cursor.execute("INSERT INTO instances VALUES (%s, %s, %s,%s)", (setup_id,ticker,dt,value))
                
            await conn.commit()
