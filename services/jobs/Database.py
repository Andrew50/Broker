import numpy as np
import  pandas as pd, numpy as np, datetime, mysql.connector, pytz, redis, pickle,  multiprocessing
import numpy as np
import  pandas as pd, os, numpy as np, time,datetime, mysql.connector, pytz, redis, pickle,  multiprocessing, json
import yfinance as yf
from mysql.connector import errorcode

import multiprocessing
import redis
import datetime
import mysql.connector


FORCE_RECALC = False
#set to True to force the recalculation of all cached data. 
#This should be done if recalc methods are changed
#allows the script to be run outside of container




class Database:
    def run():
        if FORCE_RECALC: #Only change if you neeed to recalc
            redis_conn = redis.Redis(host='localhost', port=6379)
            mysql_conn = mysql.connector.connect(host='localhost', port='3306', user='root', password='7+WCy76_2$%g',database='broker')
            Database.cache(redis_conn)
        else:
            redis_conn = redis.Redis(host='redis', port=6379)
            mysql_conn = mysql.connector.connect(host='mysql', port='3306', user='root', password='7+WCy76_2$%g')
            with mysql_conn.cursor() as cursor:
                cursor.execute("SHOW DATABASES")
                print("List of databases:")
                for (database,) in cursor:
                    print(database)
                cursor.execute(f"SHOW DATABASES LIKE 'broker'")
                database = cursor.fetchone()
                if not database:
                #try:
                #except mysql.connector.Error as err:
                    #if err.errno == errorcode.ER_BAD_DB_ERROR:
                    print('creating database', flush=True)
                    Database.setup(mysql_conn)
                    print('updating limited', flush=True)
                    Database.update(mysql_conn,10)
                    print('caching limited', flush=True)
                    Database.cache(redis_conn)
                    #$else:
                    #    raise
                else:
                    print('worked---')
                    cursor.execute("USE broker")
                #finally:
                if not os.getenv('DEV_ENV') == 'true' or not (last_update := pickle.loads(redis_conn.get("last_update"))) or datetime.datetime.now() - last_update > datetime.timedelta(days=1):
                    print('updating', flush=True)
                    Database.update(mysql_conn)
                    print('caching', flush=True)
                    Database.cache(redis_conn)

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

    ####to remove once method for pulling current ticker list exists
    def get_ticker_list():
        df = pd.read_csv('ticker_list.csv')['ticker'].tolist()
        return df

    def process_ticker_data(bars):
        mysql_host, redis_host = ('localhost', 'localhost') if FORCE_RECALC else ('mysql', 'redis')

        with redis.Redis(host=redis_host, port=6379) as redis_conn:
            with mysql.connector.connect(host=mysql_host, port='3306', user='root', password='7+WCy76_2$%g',database='broker') as mysql_conn:
                with mysql_conn.cursor() as cursor:
                    tickers,tf = bars
                    for ticker in tickers:
                        try:
                            cursor.execute("SELECT dt, open, high, low, close, volume FROM dfs WHERE ticker = %s and tf = %s", (ticker,tf))
                            data = np.array(cursor.fetchall())
                            #print(data,flush=True)
                            #for form in ('screener','chart','match'):
                            for form in ('screener','chart'):
                                if form == 'screener':
                                    dt = data[1:,0]
                                    vol = data[1:,5]
                                    dt = dt.reshape(-1,1)
                                    normalized_data = (data[1:,1:5] / data[:-1,4][:, None]) - 1
                                    normalized_data = np.column_stack((dt,normalized_data,vol))
                                    processed_data = pickle.dumps(normalized_data)
                                # elif form == 'match':
                                # 	#dt, open, high, low, close, volume 
                                # 	# 0    1     2     3     4      5
                                # 	ohlcData = data[1:,1:5]/data[:-1, 4].reshape(-1, 1) - 1
                                # 	mean = np.mean(ohlcData, axis=0)
                                # 	std = np.std(ohlcData, axis=0)
                                # 	ohlcData = (ohlcData - mean) / std

                                # 	processed_data = pickle.dumps(np.column_stack((data[1:, 0], data[1:, 4], ohlcData[:, 0], ohlcData[:, 1], ohlcData[:, 2], ohlcData[:, 3], data[1:, 5])))
                                # 	#close_prices = data[:, 4]
                                # 	#return pickle.dumps(np.column_stack((data[1:, 0], close_prices[1:], (data[1:, 1] / close_prices[:-1] - 1), (data[1:, 2]/close_prices[:-1] -1), (data[1:,3]/close_prices[:-1] - 1), (close_prices[1:] / close_prices[:-1]) - 1, data[1:, 5])))

                                elif form == 'chart':
                                    list_of_lists = data.tolist()[:]
                                    if 'd' in tf or 'w' in tf:
                                        list_of_lists = [{
                                            'time': pd.to_datetime(row[0], unit='s').strftime('%Y-%m-%d'),
                                            'open': row[1],
                                            'high': row[2],
                                            'low': row[3],
                                            'close': row[4]
                                            } for row in list_of_lists]
                                    else:
                                        list_of_lists = [{
                                            'time': pd.to_datetime(row[0], unit='s').strftime('%Y-%m-%d %H:%M:%S'),
                                            'open': row[1],
                                            'high': row[2],    
                                            'low': row[3],
                                            'close': row[4]
                                            }for row in list_of_lists]
                                    processed_data = json.dumps(list_of_lists)
                                redis_conn.hset(tf+form, ticker, processed_data)
                        except Exception as e:
                            print(f'{ticker} failed: {e}', flush=True)




    # Main Function
    def cache(redis_conn):
        tickers = Database.get_ticker_list()  # get_unique_tickers()  # Define this function to get tickers from your DB
        pool = multiprocessing.Pool(processes=8)  # Adjust number of processes as needed

        batch_size = 200
        num_batches = len(tickers) // batch_size + 1
        for tf in ('1d',):
            arglist = []

            for i in range(num_batches):
                start_index = i * batch_size
                end_index = (i + 1) * batch_size
                batch_tickers = tickers[start_index:end_index]
                arglist.append([batch_tickers, tf])

            pool.map(Database.process_ticker_data, arglist)

        pool.close()
        pool.join()
        redis_conn.set("last_update", pickle.dumps(datetime.datetime.now()))

    def update(mysql_conn,num_tickers = None):


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



        with mysql_conn.cursor(buffered=True) as cursor:

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

            full_ticker_list = Database.get_ticker_list()[:num_tickers]
            for ticker in full_ticker_list:
                for tf in ['1d']:
                    try:
                        if tf == '1d':

                            ytf = '1d'
                            period = '25y'
                        elif tf == '1min':
                            ytf = '1m'
                            period = '5d'
                        else:
                            raise Exception('invalid timeframe to update')
                        ydf = yf.download(tickers = ticker, period = period, group_by='ticker', interval = ytf, ignore_tz = True, auto_adjust=True, progress=False, show_errors = False, threads = True, prepost = True) 
                        #print(ydf)
                        #ydf.drop(axis=1, labels="Adj Close",inplace = True)
                        ydf.dropna(inplace = True)
                        if Database.is_market_open() == 1: ydf.drop(ydf.tail(1).index,inplace=True)
                        ydf.index = ydf.index.normalize() + pd.Timedelta(minutes = 570)
                        ydf.index = (ydf.index.astype(np.int64) // 10**9)
                        cursor.execute("SELECT MAX(dt) FROM dfs WHERE ticker = %s AND tf = %s", (ticker, tf))
                        result = cursor.fetchone()
                        last_day = result[0] if result else 0

                        if type(last_day) == int:
                            index = findex(ydf, last_day) 
                            ydf = ydf[index + 1:]
                        ydf.reset_index(inplace = True)

                        ydf = ydf.values.tolist()
                        ydf = [[ticker, tf] + row for row in ydf]
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
                        mysql_conn.commit()
                    except Exception as e:
                        print(f'{ticker} failed: {e}', flush=True)
                        print(ydf)


    def setup(mysql_conn):

        with mysql_conn.cursor(buffered=True) as cursor:
            cursor.execute("CREATE DATABASE broker DEFAULT CHARACTER SET 'utf8';")
            mysql_conn.commit()
            cursor.execute("USE broker;")
            mysql_conn.commit()
            sql_commands = """
            CREATE TABLE dfs(
                    ticker VARCHAR(5) NOT NULL,
                    tf VARCHAR(3) NOT NULL,
                    dt INT NOT NULL,
                    open FLOAT,
                    high FLOAT,
                    low FLOAT,
                    close FLOAT,
                    volume FLOAT,
                    PRIMARY KEY (ticker, tf, dt)
                    );
            CREATE INDEX ticker_index ON dfs (ticker);
            CREATE INDEX tf_index ON dfs (tf);
            CREATE INDEX dt_index ON dfs (dt);
            CREATE TABLE users(
                    id INT AUTO_INCREMENT PRIMARY KEY,
                    email VARCHAR(255) NOT NULL UNIQUE,
                    password VARCHAR(255),
                    settings TEXT
                    );
            CREATE INDEX email_index ON users(email);
            CREATE TABLE watchlists (
                    user_id INT,
                    name VARCHAR(255) NOT NULL,
                    ticker VARCHAR(5) NOT NULL,
                    FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE,
                    UNIQUE(user_id,name)
                    );

            CREATE INDEX user_id_index ON watchlists (user_id);
            CREATE INDEX name_index ON watchlists (name);


            CREATE TABLE study (
                    user_id INT,
                    st VARCHAR(255) NOT NULL,
                    ticker VARCHAR(5) NOT NULL,
                    dt INT NOT NULL,
                    annotation TEXT,
                    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
                    UNIQUE(user_id, st)
                    ) ;
            CREATE INDEX user_id_index ON study (user_id);
            CREATE INDEX st_index ON study (st);
            CREATE TABLE setups(
                    user_id INT NOT NULL,
                    name VARCHAR(255) NOT NULL,
                    setup_id INT AUTO_INCREMENT UNIQUE,
                    tf VARCHAR(3) NOT NULL,
                    setup_length INT NOT NULL,
                    sample_size INT,
                    score INT,
                    UNIQUE(user_id, name),
                    FOREIGN KEY (user_id) REFERENCES users(id)
                    ON DELETE CASCADE
                    );
            CREATE INDEX user_id_index ON setups (user_id);
            CREATE INDEX name_index ON setups (name);
            CREATE TABLE setup_data(
                    setup_id INT NOT NULL,
                    ticker VARCHAR(5) NOT NULL,
                    dt INT NOT NULL,
                    value BOOLEAN NOT NULL,
                    UNIQUE(setup_id,ticker, dt),
                    FOREIGN KEY (setup_id) REFERENCES setups(setup_id)
                    ON DELETE CASCADE
                    );
            CREATE INDEX id_index ON setup_data (setup_id);
            CREATE TABLE full_ticker_list(ticker VARCHAR(5) NOT NULL UNIQUE);
            """
            commands = [cmd.strip() for cmd in sql_commands.split(';') if cmd.strip()]
            for command in commands:cursor.execute(command)
            mysql_conn.commit()

            def set_setup(user_id,st,tf=None,setup_length = None,delete=False):
                with mysql_conn.cursor() as cursor:
                    if delete:
                        cursor.execute("DELETE FROM setups WHERE user_id = %s AND name = %s", (user_id,st))
                    elif tf != None and setup_length != None:
                        insert_query = "INSERT INTO setups (user_id, name, tf, setup_length) VALUES (%s, %s, %s, %s)"
                        cursor.execute(insert_query, (user_id,st,tf,setup_length))
                    else:
                        raise Exception('missing args')
                mysql_conn.commit()


            def get_user(email, password):
                with mysql_conn.cursor() as cursor:
                    cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
                    user_data = cursor.fetchone()
                    if user_data and len(user_data) > 0:
                        if password == user_data[2]:  # Assuming password is at index 2
                            return user_data[0]  



            def set_user(user_id=None, email=None, password=None, settings_string=None, delete=False):
                with mysql_conn.cursor() as cursor:
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
                                cursor.execute(update_query, values)
                        else:
                            cursor.execute("DELETE FROM users WHERE id = %s", (user_id,))
                    else:
                        insert_query = "INSERT INTO users (email, password, settings) VALUES (%s, %s, %s)"
                        cursor.execute(insert_query, (email, password, settings_string if settings_string is not None else ''))
                mysql_conn.commit()

            def set_setup_sample(user_id,st,data):##################################### ix this shit bruhhg dododosoosdodsfdsiho
                with mysql_conn.cursor(buffered=True) as cursor:
                    cursor.execute('SELECT setup_id from setups WHERE user_id = %s AND name = %s',(user_id,st))
                    setup_id = cursor.fetchone()[0]
                    print(setup_id)
                    query = [[setup_id,ticker,dt,classification] for ticker,dt,classification in data]
                    #cursor.executemany("INSERT IGNORE INTO setup_data VALUES (%s, %s, %s,%s)", query)
                    cursor.executemany("INSERT INTO setup_data VALUES (%s, %s, %s,%s)", query)
                mysql_conn.commit()

            set_user(email='user',password='pass')
            user_id = get_user('user','pass')
            path = 'instances/'
            dirs = os.listdir(path)
            for f in dirs:
                st = f.split('.')[0]
                df = pd.read_feather(path+f)
                df = df[['ticker','dt','value']]
                df['dt'] = df['dt'].astype(str).apply(Database.format_datetime)
                df = df.values.tolist()
                set_setup(user_id,st,tf='1d',setup_length = 50)
                set_setup_sample(user_id,st,df)
            print('setting isntances')

if __name__ == "__main__":
    Database.run()

