-- @block 
CREATE TABLE dfs(
    ticker VARCHAR(5) NOT NULL,
    tf VARCHAR(3) NOT NULL,
    dt INT NOT NULL,
    open DECIMAL(10, 4),
    high DECIMAL(10, 4),
    low DECIMAL(10, 4),
    close DECIMAL(10, 4),
    volume FLOAT
);
-- @block
CREATE TABLE setup_data(
    id INT NOT NULL,
    ticker VARCHAR(5) NOT NULL,
    dt INT NOT NULL
);
-- @block
CREATE TABLE setups(
    id INT NOT NULL,
    setup_id INT NOT NULL,
    name VARCHAR(255) NOT NULL,
    tf VARCHAR(3) NOT NULL,
);
-- @block
CREATE TABLE users(
    id INT PRIMARY KEY,
    setups_id INT NOT NULL,
    email VARCHAR(255),
    password VARCHAR(255),
    settings TEXT
) -- @block
CREATE TABLE users(user_id INT PRIMARY KEY,) -- @block
DROP TABLE dfs;
-- @block
select *
from users;