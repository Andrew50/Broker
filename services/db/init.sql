CREATE TABLE tickers (
    ticker_id SMALLSERIAL PRIMARY KEY,
    ticker VARCHAR(10) NOT NULL UNIQUE
);
CREATE INDEX idx_ticker ON tickers (ticker);
--1 minute extended
CREATE TABLE quotes_1_extended (
    ticker_id INTEGER NOT NULL,
    extended_hours BOOLEAN NOT NULL,
    t TIMESTAMP NOT NULL,
    open FLOAT NOT NULL,
    high FLOAT NOT NULL,
    low FLOAT NOT NULL,
    close FLOAT NOT NULL,
    volume FLOAT NOT NULL,
    FOREIGN KEY (ticker_id) REFERENCES tickers(ticker_id) ON DELETE CASCADE,
    PRIMARY KEY (ticker_id, t)
);
CREATE INDEX idx_quotes_1_extended ON quotes_1_extended (ticker_id, t) 
WHERE NOT extended_hours;
SELECT create_hypertable('quotes_1_extended', 't', 'ticker_id', 100);
--hourly extended hours
CREATE MATERIALIZED VIEW quotes_h_extended
WITH (timescaledb.continuous) AS
SELECT 
    ticker_id,
    time_bucket('1 hour', t) AS t,
    first(open, t) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, t) AS close,
    sum(volume) AS volume
FROM quotes_1_extended
GROUP BY ticker_id, time_bucket('1 hour', t)
WITH NO DATA;
SELECT add_continuous_aggregate_policy('quotes_h_extended',
    start_offset => INTERVAL '2000 years',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');
--hourly regular hours
CREATE MATERIALIZED VIEW quotes_h
WITH (timescaledb.continuous) AS
SELECT 
    ticker_id,
    --time_t('1 hour', date_trunc('hour', t - INTERVAL '30 minutes')) + INTERVAL '30 minutes' AS t,
    time_bucket('1 hour', t) AS t,
    first(open, t) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, t) AS close,
    sum(volume) AS volume
FROM quotes_1_extended
WHERE NOT extended_hours
GROUP BY ticker_id, time_bucket('1 hour', t)
WITH NO DATA;
SELECT add_continuous_aggregate_policy('quotes_h',
    start_offset => INTERVAL '2000 years',
    end_offset => INTERVAL '1 hour',
    schedule_interval => INTERVAL '1 hour');
--daily
CREATE MATERIALIZED VIEW quotes_d
WITH (timescaledb.continuous) AS
SELECT 
    ticker_id,
    time_bucket('1 day', t) AS t,
    first(open, t) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, t) AS close,
    sum(volume) AS volume
FROM quotes_1_extended
WHERE NOT extended_hours
GROUP BY ticker_id, time_bucket('1 day', t)
WITH NO DATA;
SELECT add_continuous_aggregate_policy('quotes_d',
    start_offset => INTERVAL '2000 years',
    end_offset => INTERVAL '1 day',
    schedule_interval => INTERVAL '1 day');
--weekly
CREATE MATERIALIZED VIEW quotes_w
WITH (timescaledb.continuous) AS
SELECT 
    ticker_id,
    time_bucket('1 week', t) AS t,
    first(open, t) AS open,
    max(high) AS high,
    min(low) AS low,
    last(close, t) AS close,
    sum(volume) AS volume
FROM quotes_1_extended
WHERE NOT extended_hours
GROUP BY ticker_id, time_bucket('1 week', t)
WITH NO DATA;
SELECT add_continuous_aggregate_policy('quotes_w',
    start_offset => INTERVAL '2000 years',
    end_offset => INTERVAL '1 week',
    schedule_interval => INTERVAL '1 week');


CREATE TABLE users (
    user_id SERIAL PRIMARY KEY,
    username VARCHAR(100) UNIQUE NOT NULL,
    password VARCHAR(100) NOT NULL,
    settings JSONB DEFAULT '{}'
);
CREATE INDEX idx_users ON users (username, password);
CREATE TABLE setups (
    setup_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    setup_name VARCHAR(100) NOT NULL,
    score INTEGER DEFAULT 0 NOT NULL,
    i VARCHAR(5) DEFAULT '1d' NOT NULL,
    bars INTEGER DEFAULT 30 NOT NULL,
    threshold INTEGER DEFAULT 30 NOT NULL,
    dolvol FLOAT DEFAULT 5000000 NOT NULL,
    adr FLOAT DEFAULT 2.5 NOT NULL,
    mcap FLOAT DEFAULT 0 NOT NULL,
    sample_size INTEGER DEFAULT 0 NOT NULL,
    changes INTEGER DEFAULT 0 NOT NULL,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE (user_id, setup_name)
);
CREATE INDEX idx_setups ON setups (user_id, setup_name);
CREATE TABLE annotations ( --use join with setups to get the setup name
    annotation_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    completed BOOLEAN NOT NULL,
    setup_id INTEGER NOT NULL,
    ticker_id INTEGER NOT NULL,
    t TIMESTAMP NOT NULL,
    entry TEXT,
    FOREIGN KEY (ticker_id) REFERENCES tickers(ticker_id) ON DELETE CASCADE,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE (setup_id,ticker_id,t)
);
CREATE INDEX idx_annotations ON annotations (user_id, completed);
CREATE TABLE studies ( --might need to change evntually if you want to get multiple or all setups for a user becuase 
    -- sorting by user will be way better
    study_id SERIAL PRIMARY KEY,
    setup_id INTEGER NOT NULL,
    completed BOOLEAN NOT NULL,
    ticker_id INTEGER NOT NULL,
    t TIMESTAMP NOT NULL,
    pre_entry TEXT,
    post_entry TEXT,
    FOREIGN KEY (setup_id) REFERENCES setups(setup_id) ON DELETE CASCADE,
    FOREIGN KEY (ticker_id) REFERENCES tickers(ticker_id) ON DELETE CASCADE,
    UNIQUE (setup_id, ticker_id, t)
);
CREATE INDEX idx_studies ON studies (setup_id, completed);
CREATE TABLE journals (
    journal_id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL,
    completed BOOLEAN NOT NULL,
    t TIMESTAMP NOT NULL,
    entry TEXT,
    FOREIGN KEY (user_id) REFERENCES users(user_id) ON DELETE CASCADE,
    UNIQUE (user_id, t)
);
CREATE INDEX idx_journals ON journals (user_id, completed);
CREATE TABLE samples (
    sample_id SERIAL PRIMARY KEY,
    setup_id INTEGER NOT NULL,
    value BOOLEAN,
    ticker_id INTEGER NOT NULL,
    t TIMESTAMP NOT NULL,
    FOREIGN KEY (setup_id) REFERENCES setups(setup_id) ON DELETE CASCADE,
    FOREIGN KEY (ticker_id) REFERENCES tickers(ticker_id) ON DELETE CASCADE,
    UNIQUE (setup_id, ticker_id, t)
);
CREATE INDEX idx_samples ON samples (setup_id, value);
COPY tickers(ticker) FROM '/postgres-data/tickers.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');    
INSERT INTO users (user_id, username, password, settings) VALUES (0, 'user', 'pass', jsonb_build_object());
INSERT INTO setups (setup_id,user_id,setup_name,i,bars,threshold,dolvol,adr,mcap) VALUES 
(1,0, 'EP', '1d', 30, .3, 5000000, 2.5, 0),
(2,0, 'F', '1d', 60, .3, 5000000, 2.5, 0),
(3,0, 'MR', '1d', 30, .3, 5000000, 2.5, 0),
(4,0, 'NEP', '1d', 30, .3, 5000000, 2.5, 0),
(5,0, 'NF', '1d', 60, .3, 5000000, 2.5, 0),
(6,0, 'NP', '1d', 30, .3, 5000000, 2.5, 0),
(7,0, 'P', '1d', 30, .3, 5000000, 2.5, 0);
CREATE TEMP TABLE temp (
    setup_id INTEGER NOT NULL,
    ticker VARCHAR(10) NOT NULL,
    t INTEGER NOT NULL,
    value BOOLEAN
);

COPY temp(setup_id,ticker,t,value) FROM '/postgres-data/samples.csv' WITH (FORMAT csv, HEADER true, DELIMITER ',');
INSERT INTO samples (setup_id, ticker_id, t, value)
SELECT
    ts.setup_id,
    t.ticker_id,
    TO_TIMESTAMP(ts.t),  -- Convert integer timestamp to TIMESTAMP
    ts.value
FROM
    temp ts
JOIN
    tickers t ON ts.ticker = t.ticker;


