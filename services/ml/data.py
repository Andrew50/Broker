import os, numpy as np, time,datetime,  pytz, redis, pickle,  multiprocessing, json, yfinance as yf, io, warnings, pandas as pd, re
warnings.filterwarnings("ignore", category=FutureWarning, message="The 'unit' keyword in TimedeltaIndex construction is deprecated")
import psycopg2, redisai

class Data:

    def __init__(self, inside_container = True):

        #if os.environ.get('INSIDE_CONTAINER', False): #inside container
        if inside_container:
            cache_host = 'cache'
            db_host = 'db'
        else:
            cache_host = 'localhost'
            db_host = 'localhost'
        while True:
            try:
                #self.cache = redis.Redis(host=cache_host, port=6379)
                self.cache = redisai.Client(host=cache_host,port=6379)
                self.db = psycopg2.connect(host=db_host,port='5432',user='postgres',password='pass')
            except  psycopg2.OperationalError:
                print("waiting for db", flush = True)
                time.sleep(5)
            else:
                break

    def check_connection(self):
        try:
            self.cache.ping()
            self.db.ping()
        except:
            print('Connection error')
            self.__init__()


    def getTickers(self):
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM tickers;")
            return cursor.fetchall()

    @staticmethod
    def format_datetime(dt,reverse=False):
        if reverse:
            return datetime.datetime.fromtimestamp(dt)
        if type(dt) == int or type(dt) == float or type(dt) == np.int64 or type(dt) == np.float64:
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
        dt = dt.timestamp()
        return dt

    @staticmethod
    def findex(df, dt):
#        dt = Data.format_datetime(dt)
        i = int(len(df)/2)      
        k = int(i/2)
        while k != 0:
            #date = df.index[i]
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
            if i < 0:
                raise TimeoutError
        return i
    
    @staticmethod
    def is_market_open(pm = False):
        dt = datetime.datetime.now(pytz.timezone('US/Eastern'))
        if (dt.weekday() >= 5):
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

    @staticmethod
    def getQueryInfo(interval,pm):
        match = re.match(r'(\d+)([a-zA-Z]*)', interval)
        if not match:
            raise ValueError("Invalid interval format")
        i_num, i_base =  match.groups()
        if i_base == "":
            bucket = f"{i_num} minute"
            table = "quotes_1_extended"
        elif i_base == "h":
            bucket = f"{i_num} hour"
            table = "quotes_h_pm" if pm else "quotes_h"
        elif i_base == "d":
            bucket = f"{i_num} day"
            table = "quotes_d"
        elif i_base == "w":
            bucket = f"{i_num} week"
            table = "quotes_w"
        elif i_base == "m":
            bucket = f"{i_num} month"
            table = "quotes_w"  # Possible change once we have quotes_m
        elif i_base == "y":
            bucket = f"{i_num} year"
            table = "quotes_w"  # Possible change once we have quotes_y
        else:
            raise ValueError(f"Invalid interval base: {i_base}")
        if i_num != "1" or i_base in ["m", "y"]:
            aggregate = True
        else:
            aggregate = False
        return table, bucket, aggregate

class old_Data:

    def get_trainer_queue_size(self,user_id,st):
        return self.cache.llen(str(user_id)+st)

    def set_trainer_queue(self, user_id,st, instance):
        # Add the item to the Redis list
        self.cache.lpush(str(user_id)+st, json.dumps(instance))

    def set_cache(self, format, ticker, tf, df):
        #could add the serialization here
        self.cache.hset(tf+'_'+format,ticker,df)

    @staticmethod
    def get_reqs(df,single = True):
        l = 10
        #assuming ohlcv columns
        if single: 
            dolvol = float(np.mean(df[:,3] * df[:,4]))
            adr = float(np.mean(df[-l:,1] / df[-l:,2] - 1)) * 100
            mcap = 10^15 #TODO
            return dolvol, adr, mcap
        else:
#            #TODO
            return np.array([df[i:i+20] for i in range(0,len(df),20)])
            dolvol = df[:,3] * df[:,4]
            dolvol = np.roll(dolvol,1)


    def get_df(self, form, ticker=None, tf=None, dt=None, bars=0, pm=False, df = None):
        assert (ticker and tf) or df is not None
        assert not pm 
        if bars and form in ('trainer', 'study'):
            bars += 1
        if df is None:
            if (df := self.cache.hget(f'{tf}_{form}',ticker)) is not None:
                assert not bars and not dt and not pm
                if form != 'chart':
                    df = pickle.loads(df)
                    if form == 'screener':
                        df, prev_close = df
                        try:
                            current_price = pickle.loads(self.cache.hget('current_price',ticker))
                            change = current_price / prev_close - 1
                        except TypeError:
                            print(f'{ticker} cp failed')
                            change = 0
                        df = np.vstack([df,[change for _ in range(4)]])
                return df
            else:
                if (df := self.cache.hget(f'{tf}_raw',ticker)) is None: #possible cache raw in future
                    ########################rewrite to use sql to do all this shit
                    with self.db.cursor(buffered=True) as cursor: 
                        cursor.execute("SELECT dt, open, high, low, close, volume FROM dfs WHERE ticker = %s and tf = %s", (ticker,tf))
                        df = np.array(cursor.fetchall())
                        if not df.shape[0]:
                            raise TimeoutError
                        if dt:
                            index = self.findex(df,dt)
                            df = df[:index+1,:]
                        if bars:
                            df = df[-bars:,:]
                    #####################################
        elif bars:
            df = df[-bars:,:]
        if form == 'chart':
            df = json.dumps(df.tolist())
        elif form != 'raw':
            if ticker and form == 'screener': #jank as hell
                current_price = self.cache.hget('current_price',ticker)
                change = current_price / df[-1,4] - 1
            if not ticker and form =='screener':
                prev_close = df[-1,4]
            df[1:,1:5] = df[1:,1:5] / df[:-1,4][:, None] - 1
            df[-1,2:5] = df[-1,1]
            if ticker and form == 'screener':
                df = np.vstack([df,[change for _ in range(4)]])
            if df.shape[0] < bars:
                df = np.vstack([df,[[0,0,0,0,0,0] for _ in range(bars - df.shape[0])]])
            if form == 'screener' or form == 'trainer':
                df = df[:,1:5]
            else:
                df = self.get_reqs(df,True)#TODO
            if not ticker: #jank
                if form == 'screener':
                    df = df, prev_close
                df = pickle.dumps(df)
        return df

    def set_df(self,ticker,tf,df):
        with self.db.cursor() as cursor:
            try:
                if tf == '1d':
                    ytf = '1d'
                    period = '25y'
                elif tf == '1':
                    ytf = '1m'
                    period = '5d'
                ydf = yf.download(tickers = ticker, period = period, group_by='ticker', interval = ytf, ignore_tz = True, auto_adjust=True, progress=False, show_errors = False, threads = True, prepost = True) 
                if ydf.empty:
                    return df
                ydf.dropna(inplace = True)
                if self.is_market_open():
                    ydf.drop(ydf.tail(1).index, inplace=True)
                ydf.index = ydf.index.normalize() + pd.Timedelta(minutes = 570)
                ydf.index = (ydf.index.astype(np.int64) // 10**9)
                ydf = ydf.reset_index().to_numpy()
                if df.shape[0]:
                    last_day = df[-1,0]
                    index = self.findex(ydf, last_day) 
                    ydf = ydf[index + 1:,:]
                    df = np.concatenate([df, ydf], axis=0)
                else:
                    df = ydf
                ydf = [[ticker, tf] + row for row in ydf.tolist()]
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
                self.db.commit()
                return df            
            except TimeoutError as e:
                print(f'{ticker} failed: {e}', flush=True)

    def set_setup(self,user_id,st,tf=None,setup_length = None,delete=False):
        with self.db.cursor() as cursor:
            if delete:
                cursor.execute("DELETE FROM setups WHERE user_id = %s AND name = %s", (user_id,st))
            elif tf != None and setup_length != None:
                insert_query = "INSERT INTO setups (user_id, name, tf, setup_length) VALUES (%s, %s, %s, %s)"
                cursor.execute(insert_query, (user_id,st,tf,setup_length))
            else:
                raise Exception('missing args')
        self.db.commit()


    def get_user(self,username, password):
        with self.db.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE username = %s", (username,))
            user_data = cursor.fetchone()
            if user_data and len(user_data) > 0:
                if password == user_data[2]:  # Assuming password is at index 2
                    return user_data[0]  

    def set_user(self,user_id=None, username=None, password=None, settings_string=None, delete=False):
        with self.db.cursor() as cursor:
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
                        cursor.execute(update_query, values)
                else:
                    cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
            else:
                insert_query = "INSERT INTO users (username, password, settings) VALUES (%s, %s, %s)"
                cursor.execute(insert_query, (username, password, settings_string if settings_string is not None else ''))
        self.db.commit()

    @staticmethod
    def current_price_worker(tickers):
        ds = yf.download(" ".join(tickers), interval='1m', period='1d', prepost=True, auto_adjust=True, threads=True, keepna=False)
        last_close_values = []
        for ticker in tickers:
            try:
                close_data = ds['Close', ticker]
                close_data = close_data.dropna()
                if close_data.empty:
                    raise Exception('empty')
                else:
                    last_non_na_close = close_data.iloc[-1]
                    last_close_values.append([ticker,last_non_na_close])
                    #last_close_values[ticker] = last_non_na_close
            except Exception as e:
                print(e,flush=True)
        return last_close_values

    def set_current_prices(self,tickers):
        batches = []
        pool_size = 5
        batch_size = int(len(tickers)/pool_size) + 5
        for i in range(0,len(tickers),batch_size):
            batches.append(tickers[i:i + batch_size])
        with multiprocessing.Pool(pool_size) as pool:
            results = pool.map(self.current_price_worker,batches)
        for result in results:
            for ticker, price in result:
                self.cache.hset('current_price', ticker, pickle.dumps(price))

    def get_tickers(self,type = 'full', min_dolvol = -1, min_adr = -1,min_mcap = -1):
#        df = pd.read_csv('ticker_listype='full'.csv')['ticker'].tolist()
#        if dolvol:
#            df = df[df['dollar_volume'] > dolvol]
#        if adr:
#            df = df[df['adr'] > adr]
        cursor = self.db.cursor(buffered=True)
        if type == 'current': 
            type = 'full'
        if type == 'full':
            query = "SELECT ticker FROM tickers"
            cursor.execute(query)
            data = cursor.fetchall()
            cursor.close()
            data = [item[0] for item in data]
            return data
        elif type == 'screener':
            query = "SELECT ticker, dolvol, adr, mcap FROM tickers WHERE dolvol > %s AND adr > %s AND mcap > %s"
            cursor.execute(query,(min_dolvol, min_adr, min_mcap))
            data = cursor.fetchall()
            cursor.close()
            #data = [item[0] for item in data]
            return data
        elif type == 'current': #TODO
            pass
        else:
            raise Exception('invalid type')

    def set_ticker(self, ticker, dolvol, adr, mcap):
        with self.db.cursor() as cursor:
            insert_query = """
            INSERT INTO tickers (ticker, dolvol, adr, mcap) 
            VALUES (%s, %s, %s, %s)
            ON DUPLICATE KEY UPDATE 
            adr = VALUES(adr), 
            dolvol = VALUES(dolvol), 
            mcap = VALUES(mcap)
            """
            cursor.execute(insert_query, (ticker,dolvol,adr , mcap))
        self.db.commit()

    @staticmethod
    def format_datetime(dt,reverse=False):
        if reverse:
            return datetime.datetime.fromtimestamp(dt)
        if type(dt) == int or type(dt) == float or type(dt) == np.int64 or type(dt) == np.float64:
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
        dt = dt.timestamp()
        return dt

    @staticmethod
    def is_market_open(pm = False):

        dt = datetime.datetime.now(pytz.timezone('US/Eastern'))
        if (dt.weekday() >= 5):
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

    def set_setup_info(self,user_id,st,size=None,score=None):
        for val, ident in [[size,'sample_size'],[score,'score']]:
            if val != None:
                with self.db.cursor(buffered=True) as cursor:
                    query = f"UPDATE setups SET {ident} = %s WHERE user_id = %s AND name = %s;"
                    cursor.execute(query, (val, user_id, st))
        self.db.commit()

    def get_setup(self,user_id,st):
        with self.db.cursor(buffered=True) as cursor:
            cursor.execute('SELECT setup_id,tf,setup_length,dolvol,adr,mcap from setups WHERE user_id = %s AND name = %s',(user_id,st))
            return cursor.fetchall()[0]

    def get_finished_study_tickers(self,user_id,st):
        with self.db.cursor(buffered = True) as cursor:
            query = "SELECT DISTINCT ticker FROM study WHERE user_id = %s AND st = %s"
            cursor.execute(query, (user_id, st))

            return [row[0] for row in cursor.fetchall()]

    def get_study_length(self,user_id,st):
        with self.db.cursor(buffered = True) as cursor:
            query = "SELECT COUNT(*) FROM study WHERE user_id = %s AND st = %s AND annotation <> ''"
            cursor.execute(query, (user_id, st))
            count = cursor.fetchone()[0]
        return count

    def set_study(self,user_id,st,instances):
        with self.db.cursor(buffered = True) as cursor:
            query = [[user_id,st,ticker,dt,''] for ticker,tf,dt in instances]
            cursor.executemany("INSERT INTO study VALUES (%s, %s, %s, %s, %s)",query)
        self.db.commit()

    def get_sample(self,user_id,st): #rename to get sample
        with self.db.cursor(buffered=True) as cursor:
            setup_id, tf,setup_length,_,_,_ = self.get_setup(user_id,st)
            cursor.execute('SELECT ticker,dt,value from samples WHERE setup_id = %s',(setup_id,))
            #values = [[ticker,dt,val] for setup_id,ticker,dt,val in cursor.fetchall()]
            values = cursor.fetchall()
            return values,tf,setup_length

    def set_sample(self,user_id,st,data): #rename to set sample        
        with self.db.cursor(buffered=True) as cursor:
            cursor.execute('SELECT setup_id from setups WHERE user_id = %s AND name = %s',(user_id,st))
            setup_id = cursor.fetchone()[0]
            print(setup_id)
            query = [[setup_id,ticker,dt,classification] for ticker,dt,classification in data]
            cursor.executemany("INSERT INTO samples VALUES (%s, %s, %s,%s)", query)
        self.db.commit()

#    def get_model(self,user_id,st):
#        setup_id,_,_ = self.get_setup_info(user_id,st)
#        import tensorflow as tf
#        model = self.cache.hget('models',setup_id)
#        return tf.keras.models.load_model(io.BytesIO(model))
    
#    def set_model(self,user_id,st,model):
#        setup_id,_,_ = self.get_setup_info(user_id,st)
#        #import tensorflow as tf
#        buffer = io.BytesIO()
#        model.save(buffer, save_format='h5')
#        #tf.keras.models.save_model(model, buffer, save_format='tf')
#        self.cache.hset('models',setup_id,buffer.getvalue())

    def get_model(self, user_id, st):
        import tensorflow as tf
        import io
        import tempfile

        # Get the setup ID and the model bytes from the cache
        setup_id, _, _, _, _, _ = self.get_setup(user_id, st)
        model_bytes = self.cache.hget('models', setup_id)

        # Step 1: Write the bytes to a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.h5') as tmp_file:
            temp_file_path = tmp_file.name
            tmp_file.write(model_bytes)
            tmp_file.flush()  # Ensure all data is written to disk

        # Step 2: Load the model from the temporary file
        model = tf.keras.models.load_model(temp_file_path)

        # Optionally, delete the temporary file if you want to clean up
        import os
        os.remove(temp_file_path)

        return model


    def set_model(self, user_id, st, model):
        import tensorflow as tf
        import io
        import tempfile
        setup_id, _, _,_,_,_ = self.get_setup(user_id, st)
        
        # Step 1: Save the model to a temporary HDF5 file
        with tempfile.NamedTemporaryFile(delete=False, suffix='.h5') as tmp_file:
            temp_file_path = tmp_file.name
        model.save(temp_file_path, save_format='h5')
        
        # Step 2: Read the saved model file into a bytes-like object
        with open(temp_file_path, 'rb') as model_file:
            model_bytes = model_file.read()
        
        # Step 3: Store the model in the Redis database
        self.cache.hset('models', setup_id, model_bytes)
        
        # Optionally, delete the temporary file if you want to clean up
        import os
        os.remove(temp_file_path)


    @staticmethod
    def findex(df, dt):
        dt = Data.format_datetime(dt)
        i = int(len(df)/2)      
        k = int(i/2)
        while k != 0:
            #date = df.index[i]
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
            if i < 0:
                raise TimeoutError
        return i


