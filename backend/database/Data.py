import mysql.connector
import os
import pandas as pd



class Data:

    def __init__(self,db_name='broker'):

        db = mysql.connector.connect(
            host = "localhost",
            user="root",
            passwd="7+WCy76_2$%g",
            database=db_name
        )

        self.c = db.cursor()




    def init(self):
    
        folder = 'C:/dev/Broker/backend/scripts/d/'
        dir_list = os.listdir(folder)
        for d in dir_list:
            ticker = d.split('.')[0]
            tf = '1d'
            path = folder + d
            df = pd.read_feather(path)
            df['datetime'] = df['datetime'].astype(str)
            df = df.values.tolist()
            for row in df:
                row = [ticker, tf] + row
                insert_query = "INSERT INTO dfs VALUES (%s, %s, %s, %s, %s, %s, %s, %s)"
                self.c.execute(insert_query, row)
                self.print_table('dfs')
                return


        #db.commit()
        #db.close()
    
    def print_table(self,name):
        self.c.execute(f'SELECT * FROM {name}')
        df = self.c.fetchall()
        print(df)

if __name__ == '__main__':
    db = Data()
    db.init()
    




