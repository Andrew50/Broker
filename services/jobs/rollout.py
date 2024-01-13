

import pandas as pd
import os
import datetime
import pytz


from Database import db


def set_setup_sample(self,user_id,st,data):##################################### ix this shit bruhhg dododosoosdodsfdsiho
    with self.mysql_conn.cursor(buffered=True) as cursor:
        cursor.execute('SELECT setup_id from setups WHERE user_id = %s AND name = %s',(user_id,st))
        setup_id = cursor.fetchone()[0]
        print(setup_id)
        query = [[setup_id,ticker,dt,classification] for ticker,dt,classification in data]
        #cursor.executemany("INSERT IGNORE INTO setup_data VALUES (%s, %s, %s,%s)", query)
        cursor.executemany("INSERT INTO setup_data VALUES (%s, %s, %s,%s)", query)
    self.mysql_conn.commit()


def get_user(self, email, password):
    with self.mysql_pool.acquire() as conn:
        with conn.cursor() as cursor:
            cursor.execute("SELECT * FROM users WHERE email = %s", (email,))
            user_data = cursor.fetchone()
            if user_data and len(user_data) > 0:
                if password == user_data[2]:  # Assuming password is at index 2
                    return user_data[0]

db.get_user = get_user
db.set_setup_sample = set_setup_sample


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



user_id = db.get_user('user','pass')


path = 'instances'
dirs = os.listdir(path)
for f in dirs:
    st = f.split('.')[0]
    df = pd.read_feather(path+f)
    df = df[['ticker','dt','value']]
    df['dt'] = df['dt'].astype(str).apply(format_datetime)
    df = df.values.tolist()
    db.set_setup_sample(user_id,st,df)


