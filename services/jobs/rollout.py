import mysql.connector, redis


mysql_conn = redis.Redis(host='redis', port=6379)
redis_conn = mysql.connector.connect(host='mysql',port='3306',user='root',password='7+WCy76_2$%g',database='broker')




