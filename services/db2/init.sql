CREATE TABLE tickers (
    pk SERIAL PRIMARY KEY,
    ticker VARCHAR(5) NOT NULL UNIQUE
);
--1 minute base data
CREATE TABLE quotes_1 (
    ticker VARCHAR(5) NOT NULL,
    extended_hours BOOLEAN NOT NULL,
    t TIMESTAMP NOT NULL,
    open FLOAT NOT NULL,
    high FLOAT NOT NULL,
    low FLOAT NOT NULL,
    close FLOAT NOT NULL,
    volume FLOAT NOT NULL,
    FOREIGN KEY (ticker) REFERENCES tickers(ticker) ON DELETE CASCADE,
    PRIMARY KEY (ticker, extended_hours, t)
);
SELECT create_hypertable('quotes_1', 't', 'ticker', 1);
--hourly regular hours
CREATE MATERIALIZED VIEW quotes_h_regular
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', t - INTERVAL '30 minutes') + INTERVAL '30 minutes' AS bucket,
    ticker,
    first(open, t) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, t) AS close,
    sum(volume) AS volume
FROM quotes_1
WHERE NOT extended_hours
GROUP BY bucket, ticker
WITH NO DATA;
SELECT add_continuous_aggregate_policy('quotes_h_regular',
    start_offset => INTERVAL '2 hour',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');
--hourly extended hours
CREATE MATERIALIZED VIEW quotes_h_extended
WITH (timescaledb.continuous) AS
SELECT 
    time_bucket('1 hour', t) AS bucket,
    ticker,
    first(open, t) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, t) AS close,
    sum(volume) AS volume
FROM quotes_1
GROUP BY bucket, ticker
WITH NO DATA;
SELECT add_continuous_aggregate_policy('quotes_h_extended',
    start_offset => INTERVAL '2 hour',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');
--daily
CREATE MATERIALIZED VIEW quotes_d
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 day', t) AS bucket,
    ticker,
    first(open, t) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, t) AS close,
    sum(volume) AS volume
FROM quotes_1
WHERE NOT extended_hours
GROUP BY bucket, ticker
WITH NO DATA;
SELECT add_continuous_aggregate_policy('quotes_d',
    start_offset => INTERVAL '2 day',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');
--weekly
CREATE MATERIALIZED VIEW quotes_w
WITH (timescaledb.continuous) AS
SELECT time_bucket('1 week', t) AS bucket,
    ticker,
    first(open, t) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, t) AS close,
    sum(volume) AS volume
FROM quotes_1
WHERE NOT extended_hours
GROUP BY bucket, ticker
WITH NO DATA;
SELECT add_continuous_aggregate_policy('quotes_w',
    start_offset => INTERVAL '2 week',
    end_offset => INTERVAL '1 week',
    schedule_interval => INTERVAL '1 week');


CREATE TABLE users (
    user_id SERIAL,
    username VARCHAR(100) NOT NULL,
    password VARCHAR(100) NOT NULL,
    settings JSONB,
    PRIMARY KEY (username, password)
);
CREATE TABLE setups (
    pk SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    setup_name VARCHAR(100) NOT NULL,
    score INTEGER,
    i VARCHAR(5),
    bars INTEGER,
    threshold INTEGER,
    dolvol FLOAT,
    adr FLOAT,
    mcap FLOAT,
    sample_size INTEGER,
    changes INTEGER,
    study_ticker_id INTEGER NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (study_ticker_id) REFERENCES tickers(pk) ON DELETE CASCADE
);
CREATE TABLE annotations (
    pk SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    completed BOOLEAN NOT NULL,
    ticker VARCHAR(5) NOT NULL,
    setup_name VARCHAR(100) NOT NULL,
    t TIMESTAMP NOT NULL,
    entry TEXT,
    FOREIGN KEY (ticker) REFERENCES tickers(ticker) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    FOREIGN KEY (setup_name) REFERENCES setups(setup_name) ON DELETE CASCADE,
    INDEX (user_id, completed)
);
CREATE TABLE studies (
    pk SERIAL PRIMARY KEY,
    setup_id INTEGER NOT NULL,
    completed BOOLEAN NOT NULL,
    ticker VARCHAR(5) NOT NULL,
    t TIMESTAMP NOT NULL,
    pre_annotation TEXT,
    post_annotation TEXT,
    FOREIGN KEY (setup_id) REFERENCES setups(pk) ON DELETE CASCADE,
    FOREIGN KEY (ticker) REFERENCES tickers(ticker) ON DELETE CASCADE,
    INDEX (setup_id, completed)
);
CREATE TABLE samples (
    pk SERIAL PRIMARY KEY,
    setup_id INTEGER NOT NULL,
    value BOOLEAN,
    ticker VARCHAR(5) NOT NULL,
    t TIMESTAMP NOT NULL,
    INDEX (setup_id, value),
    FOREIGN KEY (setup_id) REFERENCES setups(pk) ON DELETE CASCADE,
    FOREIGN KEY (ticker) REFERENCES tickers(ticker) ON DELETE CASCADE
);
    
