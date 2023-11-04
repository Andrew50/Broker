-- @block 
DROP TABLE IF EXISTS setup_data;
DROP TABLE IF EXISTS setups;
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS dfs;
DROP TABLE IF EXISTS full_ticker_list;
DROP TABLE IF EXISTS current_ticker_list;
-- print a table
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
    email VARCHAR(255),
    password VARCHAR(255),
    settings TEXT
);
CREATE TABLE setups(
    user_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    setup_id INT NOT NULL UNIQUE,
    tf VARCHAR(3) NOT NULL,
    model BINARY,
    FOREIGN KEY (user_id) REFERENCES users(id)
);
CREATE INDEX user_id_index ON setups (user_id);
CREATE INDEX name_index ON setups (name);
CREATE TABLE setup_data(
    setup_id INT NOT NULL,
    ticker VARCHAR(5) NOT NULL,
    dt INT NOT NULL,
    FOREIGN KEY (setup_id) REFERENCES setups(setup_id)
);
CREATE INDEX id_index ON setup_data (setup_id);
CREATE TABLE full_ticker_list(ticker VARCHAR(5) NOT NULL);
CREATE TABLE current_ticker_list(ticker VARCHAR(5) NOT NULL);
-- @block
SELECT *
FROM dfs
WHERE ticker = "AAPL"