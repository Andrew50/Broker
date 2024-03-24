CREATE DATABASE IF NOT EXISTS broker;
USE broker;
CREATE TABLE dfs(
        ticker VARCHAR(5) NOT NULL,
        tf VARCHAR(3) NOT NULL,
        dt INT NOT NULL,
        open FLOAT,
        high FLOAT,
        low FLOAT,
        close FLOAT,
        volume FLOAT,
        PRIMARY KEY (ticker, tf, dt)
        );
CREATE INDEX ticker_index ON dfs (ticker);
CREATE INDEX tf_index ON dfs (tf);
CREATE INDEX dt_index ON dfs (dt);
CREATE TABLE users(
        id INT AUTO_INCREMENT PRIMARY KEY,
        username VARCHAR(255) NOT NULL UNIQUE,
        password VARCHAR(255),
        settings TEXT
        );
CREATE INDEX username_index ON users(username);
CREATE TABLE watchlists(
        user_id INT,
        name VARCHAR(255) NOT NULL,
        ticker VARCHAR(5) NOT NULL,
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE,
        UNIQUE(user_id,name)
        );
CREATE INDEX user_id_index ON watchlists (user_id);
CREATE INDEX name_index ON watchlists (name);
CREATE TABLE study(
        user_id INT,
        st VARCHAR(255) NOT NULL,
        ticker VARCHAR(5) NOT NULL,
        dt INT NOT NULL,
        annotation TEXT,
        FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
        UNIQUE(user_id, st)
        );
CREATE INDEX user_id_index ON study (user_id);
CREATE INDEX st_index ON study (st);
CREATE TABLE setups(
        user_id INT NOT NULL,
        name VARCHAR(255) NOT NULL,
        setup_id INT AUTO_INCREMENT UNIQUE,
        tf VARCHAR(3) NOT NULL,
        setup_length INT NOT NULL,
        sample_size INT,
        score INT,
        dolvol FLOAT,
        adr FLOAT,
        mcap FLOAT,
        UNIQUE(user_id, name),
        FOREIGN KEY (user_id) REFERENCES users(id)
        ON DELETE CASCADE
        );
CREATE INDEX user_id_index ON setups (user_id);
CREATE INDEX name_index ON setups (name);
CREATE TABLE samples(
        setup_id INT NOT NULL,
        ticker VARCHAR(5) NOT NULL,
        dt INT NOT NULL,
        value BOOLEAN NOT NULL,
        UNIQUE(setup_id,ticker, dt),
        FOREIGN KEY (setup_id) REFERENCES setups(setup_id)
        ON DELETE CASCADE
        );
CREATE INDEX id_index ON samples(setup_id);
CREATE TABLE tickers(
        ticker VARCHAR(8) NOT NULL UNIQUE,
        dolvol FLOAT,
        adr FLOAT,
        mcap FLOAT
        );
INSERT INTO users (id, username, password, settings) VALUES (1, 'user', 'pass', '');
INSERT INTO setups (user_id, name, setup_id, tf, setup_length, sample_size, score, dolvol, adr, mcap) VALUES 
    (1, 'EP', 1, '1d', 30, 0, 0,5000000,2.5,0),
    (1, 'F', 2, '1d', 30, 0, 0,5000000,2.5,0),
    (1, 'MR', 3, '1d', 30, 0, 0,5000000,2.5,0),
    (1, 'NEP', 4, '1d', 30, 0, 0,5000000,2.5,0),
    (1, 'NF', 5, '1d', 60, 0, 0,5000000,2.5,0),
    (1, 'NP', 6, '1d', 60, 0, 0,5000000,2.5,0),
    (1, 'P', 7, '1d', 30, 0, 0,5000000,2.5,0);
LOAD DATA INFILE '/var/lib/mysql-files/tickers.csv' INTO TABLE tickers FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 ROWS (ticker);
LOAD DATA INFILE '/var/lib/mysql-files/samples.csv' INTO TABLE samples FIELDS TERMINATED BY ',' LINES TERMINATED BY '\n' IGNORE 1 ROWS;
