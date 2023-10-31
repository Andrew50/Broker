import mysql.connector
import os
import pandas as pd
from multiprocessing import Pool
from tqdm import tqdm
import numpy as np
from decimal import Decimal
import datetime

class Data:
    def __init__(self):
        self.folder = 'C:/dev/Broker/backend/tasks/d/'
        self.db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="7+WCy76_2$%g",
            database='Broker',
            autocommit=True  # Enable autocommit
        )
        self.c = self.db.cursor()
        


    def setup_db(self):
        
        command = '''
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
        '''




        # Splitting the script by '-- @block' to separate individual commands
        # commands = sql_script.split('-- @block')
        # for command in commands:
        #     # Strip leading and trailing whitespaces and skip empty commands
        #     command = command.strip()
        #     if command:
        try:
            self.c.execute(command)
        except mysql.connector.Error as err:
            print("Error executing command:", command)
            print("Error:", err)

    @staticmethod
    def insert_data(args):
        ticker, tf, df = args
        try:
            db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="7+WCy76_2$%g",
            database='Broker',
            autocommit=True
        )
        except:
            Data.setup_db()
            db = mysql.connector.connect(
            host="localhost",
            user="root",
            passwd="7+WCy76_2$%g",
            database='Broker',
            autocommit=True
        )
        c = db.cursor()
        #df['datetime'] = pd.to_datetime(df['datetime'])
        df['datetime'] = df['datetime'].astype(str)
        df = df.values.tolist()

        for row in df:
            row = [ticker, tf] + row
            insert_query = "INSERT IGNORE INTO dfs VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
            c.execute(insert_query, row)
        
        c.close()
        db.close()

    def install(self):
        try:
            self.c.execute("TRUNCATE TABLE dfs")
        except:
            pass
        dir_list = os.listdir(self.folder)[:500]
        if len(dir_list) < 10:
            raise Exception('dont have data')

        with Pool() as pool:
            args = []
            for d in dir_list:
                ticker = d.split('.')[0]
                tf = '1d'
                path = self.folder + d
                df = pd.read_feather(path)
                args.append((ticker, tf, df))
            list(tqdm(pool.imap_unordered(self.insert_data, args), total=len(args)))

    def get_data(self, ticker, tf='1d',dt=None):
        if dt != None:
            query = "SELECT * FROM dfs WHERE ticker = %s AND tf = %s AND dt = %s"
            self.c.execute(query, (ticker, tf,dt))
        else: 
            query = "SELECT * FROM dfs WHERE ticker = %s AND tf = %s"
            self.c.execute(query, (ticker, tf))
        data = self.c.fetchall()
        if data:
            
            columns = ['ticker', 'timeframe', 'datetime', 'open', 'high', 'low', 'close', 'volume']

            # Convert the list of tuples to a Pandas DataFrame
            df = pd.DataFrame(data, columns=columns)

            # Convert 'date' column to datetime
            
            df['datetime'] = pd.to_datetime(df['datetime'])

            # Rename 'date' column to 'datetime'

            # Reorder columns to have 'datetime' first
            cols = ['datetime'] + [col for col in df if col != 'datetime']
            df = df[cols]

            # Drop 'ticker' and 'timeframe' columns
            df = df.drop(columns=['ticker', 'timeframe'])
            df.set_index('datetime',inplace = True)
            df[['open', 'high', 'low', 'close']] = df[['open', 'high', 'low', 'close']].applymap(float)
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
    #print(db.get_data('A')




