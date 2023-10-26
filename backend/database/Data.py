import mysql.connector

db = mysql.connector.connect(
    host = "localhost",
    user="root",
    passwd="7+WCy76_2$%g",
    database='broker'
)

c = db.cursor()




def init():
    df = c.execute('SELECT * FROM dfs')
    print(df)
    


if __name__ == '__main__':
    init()




