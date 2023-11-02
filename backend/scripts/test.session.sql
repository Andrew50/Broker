-- @block 
DROP TABLE IF EXISTS users;
DROP TABLE IF EXISTS setups;
DROP TABLE IF EXISTS setup_data;
DROP TABLE IF EXISTS dfs;
-- print a table
CREATE TABLE dfs(
    ticker VARCHAR(5) NOT NULL,
    tf VARCHAR(3) NOT NULL,
    dt DATETIME NOT NULL,
    open DECIMAL(10, 4),
    high DECIMAL(10, 4),
    low DECIMAL(10, 4),
    close DECIMAL(10, 4),
    volume FLOAT,
    PRIMARY KEY (ticker, tf, dt)
);
CREATE TABLE setup_data(
    id INT NOT NULL,
    ticker VARCHAR(5) NOT NULL,
    dt INT NOT NULL
);
CREATE INDEX id_index ON setup_data (id);
CREATE TABLE setups(
    id INT NOT NULL,
    setup_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    tf VARCHAR(3) NOT NULL,
    FOREIGN KEY (setup_id) REFERENCES setup_data(id)
);
CREATE INDEX id_index ON setups (id);
CREATE TABLE users(
    id INT PRIMARY KEY,
    setups_id INT NOT NULL,
    email VARCHAR(255),
    password VARCHAR(255),
    settings TEXT,
    FOREIGN KEY (setups_id) REFERENCES setups(id)
);
CREATE TABLE full_ticker_list(ticker VARCHAR(5) NOT NULL);
-- @block
SELECT *
FROM dfs
WHERE ticker = "AAPL"