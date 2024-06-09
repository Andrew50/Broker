#Dockerfile
FROM timescale/timescaledb:latest-pg14
ARG CONF_FILE=dev
COPY init/${CONF_FILE}.conf /etc/postgresql/postgresql.conf
ENV POSTGRES_PASSWORD=pass
COPY init/init.sql /docker-entrypoint-initdb.d/01_init.sql
COPY init/init.sh /docker-entrypoint-initdb.d/02_init.sh
RUN chmod +x /docker-entrypoint-initdb.d/02_init.sh
COPY data/samples.csv /postgres-data/
COPY data/tickers.csv /postgres-data/
#COPY quotes/ /postgres-data/quotes/
EXPOSE 5432

CMD ["postgres", "-c", "config_file=/etc/postgresql/postgresql.conf"]
