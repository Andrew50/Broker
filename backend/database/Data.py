import mysql.connector

db = mysql.connector.connect(
    host = "localhost",
    user="root",
    passwd="7+WCy76_2$%g",
)
mycursor = db.cursor()
mycursor.execute("CREATE DATABASE testdatabase")





