-- This line creates a new database called 'venues' if it doesn't already exist.
CREATE DATABASE IF NOT EXISTS venues;

-- This line drops the user 'localuser' if it already exists.
DROP USER IF EXISTS 'localuser'@'localhost';

-- This line creates a new user called 'localuser' with the password 'localpassword'.
CREATE USER 'localuser'@'localhost' IDENTIFIED BY 'localpassword';

-- This line grants all privileges on the 'venues' database to the 'localuser' user.
GRANT ALL PRIVILEGES ON venues . * TO 'localuser'@'localhost';

-- This line reloads the privileges from the grant tables in the mysql database.
FLUSH PRIVILEGES;

-- This line switches to the 'venues' database.CREATE TABLE info (
USE venues;
    `id` BIGINT,
    `venue_id` BIGINT,
    `conversions_per_impression` DOUBLE,
    `price_range` TINYINT,
    `rating` FLOAT,
    `popularity` DOUBLE,
    `retention_rate` DOUBLE,
    PRIMARY KEY (`venue_id`),
    UNIQUE KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
