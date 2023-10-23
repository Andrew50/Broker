/*INSERT INTO Users (email, bio, country)
 VALUES(
 'hello@world.com',
 'i love strangers!',
 'US'
 );*/
--multiple rows with commas
--@block
SELECT email
From Users
    /*  */
    /*INSERT INTO Users (email, bio, country)
     VALUES(
     
     'hola@munda.com', 'bar', 'MX'),
     ('bonjour@monde.com', 'baz', 'FR'
     );*/
    /* SELECT email,
     id
     FROM Users
     WHERE country = 'US'
     AND email LIKE 'h%'
     ORDER BY id ASC
     LIMIT 2; */
    /*CREATE TABLE Users(
     id INT PRIMARY KEY AUTO_INCREMENT,
     email VARCHAR(255) NOT NULL UNIQUE,
     bio TEXT,
     country VARCHAR(2)
     );*/