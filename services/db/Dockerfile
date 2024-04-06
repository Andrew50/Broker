FROM timescale/timescaledb:latest-pg14
ENV POSTGRES_PASSWORD=pass
COPY init.sql /docker-entrypoint-initdb.d/
COPY samples.csv /postgres-data/
COPY tickers.csv /postgres-data/
ARG CONF_FILE=dev
COPY ${CONF_FILE}.conf /etc/postgresql/postgresql.conf
EXPOSE 5432


