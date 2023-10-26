-- @block 
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
-- @block
CREATE TABLE setup_data(
    id INT NOT NULL,
    ticker VARCHAR(5) NOT NULL,
    dt INT NOT NULL
);
CREATE INDEX id_index ON setup_data (id);
-- @block
CREATE TABLE setups(
    id INT NOT NULL,
    setup_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    tf VARCHAR(3) NOT NULL,
    FOREIGN KEY (setup_id) REFERENCES setup_data(id)
);
CREATE INDEX id_index ON setups (id);
-- @block
CREATE TABLE users(
    id INT PRIMARY KEY,
    setups_id INT NOT NULL,
    email VARCHAR(255),
    password VARCHAR(255),
    settings TEXT,
    FOREIGN KEY (setups_id) REFERENCES setups(id)
);
-- @block
DROP TABLE dfs;
DROP TABLE setup_data;
DROP TABLE setups;
DROP TABLE users;
-- @block
INSERT INTO dfs
VALUES ('AAPL', 'd', 0, 10, 11, 9, 10, 100);
-- @block
select *
from dfs;
-- @block
DELETE FROM dfs;