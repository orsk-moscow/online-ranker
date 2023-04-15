CREATE DATABASE IF NOT EXISTS venues;
DROP USER IF EXISTS 'localuser'@'localhost';
CREATE USER 'localuser'@'localhost' IDENTIFIED BY 'localpassword';
GRANT ALL PRIVILEGES ON venues . * TO 'localuser'@'localhost';
FLUSH PRIVILEGES;

USE venues;
 
CREATE TABLE info (
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
