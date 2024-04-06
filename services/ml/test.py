
import psycopg2
conn = psycopg2.connect(host='localhost',port='5432',user='postgres',password='pass')

with conn.cursor() as cursor:
    #cursor.execute("SELECT * FROM quotes_1 WHERE ticker_id = 1 LIMIT 10;")
    cursor.execute("SELECT * FROM quotes_h_extended WHERE ticker_id = 1 LIMIT 50;")
    quotes = cursor.fetchall()

    print(quotes)
