/*INSERT INTO Users (email, bio, country)
 VALUES(
 'hello@world.com',
 'i love strangers!',
 'US'
 );*/
--multiple rows with commas
--@block
/*INSERT INTO Users (email, bio, country)
 VALUES(
 
 'hola@munda.com', 'bar', 'MX'),
 ('bonjour@monde.com', 'baz', 'FR'
 );*/
SELECT email,
    id
FROM Users
WHERE country = 'US'
    AND id > 0
ORDER BY id ASC
LIMIT 2;
/*CREATE TABLE Users(
 id INT PRIMARY KEY AUTO_INCREMENT,
 email VARCHAR(255) NOT NULL UNIQUE,
 bio TEXT,
 country VARCHAR(2)
 );*/