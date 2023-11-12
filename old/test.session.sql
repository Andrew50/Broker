-- @block 
DROP TABLE IF EXISTS setup_data;
DROP TABLE IF EXISTS setups;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS dfs;
DROP TABLE IF EXISTS full_ticker_list;
DROP TABLE IF EXISTS current_ticker_list;
CREATE TABLE dfs(
    ticker VARCHAR(5) NOT NULL,
    tf VARCHAR(3) NOT NULL,
    dt INT NOT NULL,
    open DECIMAL(10, 4),
    high DECIMAL(10, 4),
    low DECIMAL(10, 4),
    close DECIMAL(10, 4),
    volume FLOAT,
    PRIMARY KEY (ticker, tf, dt)
);
CREATE INDEX ticker_index ON dfs (ticker);
CREATE INDEX tf_index ON dfs (tf);
CREATE INDEX dt_index ON dfs (dt);
CREATE TABLE users(
    id INT AUTO_INCREMENT PRIMARY KEY,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255),
    settings TEXT
);
CREATE INDEX email_index ON users(email);
CREATE TABLE setups(
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    setup_id INT AUTO_INCREMENT UNIQUE,
    tf VARCHAR(3) NOT NULL,
    model BINARY,
    UNIQUE(user_id, name),
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX user_id_index ON setups (user_id);
CREATE INDEX name_index ON setups (name);
CREATE TABLE setup_data(
    setup_id INT NOT NULL,
    ticker VARCHAR(5) NOT NULL,
    dt INT NOT NULL,
    value BOOLEAN NOT NULL,
    UNIQUE(ticker, dt),
    FOREIGN KEY (setup_id) REFERENCES setups(setup_id)
);
CREATE INDEX id_index ON setup_data (setup_id);
CREATE TABLE full_ticker_list(ticker VARCHAR(5) NOT NULL);
CREATE TABLE current_ticker_list(ticker VARCHAR(5) NOT NULL);
-- @block
SELECT *
FROM setup_data;
-- @block
SELECT *
FROM dfs -- @block
SELECT *
FROM users --@block
SELECT *
FROM dfs
WHERE ticker = 'AAPL'
    AND tf = '1d'
ORDER BY dt ASC