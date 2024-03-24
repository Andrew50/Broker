FROM mysql:latest
ENV MYSQL_ROOT_PASSWORD=7+WCy76_2$%g
COPY init.sql /docker-entrypoint-initdb.d/
COPY samples.csv /var/lib/mysql-files/
COPY tickers.csv /var/lib/mysql-files/
