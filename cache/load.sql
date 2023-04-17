-- Switch to the `venues` database.
USE venues;

-- Load data from the specified csv file into the `info` table.
-- The `LOCAL` keyword indicates that the file is located on the client machine, not the server.
-- The `INFILE` keyword specifies the path to the file.
-- The `FIELDS TERMINATED BY` clause specifies the delimiter used in the file.
-- The `IGNORE 1 ROWS` clause tells MySQL to skip the first row of the file, which usually contains the header.
LOAD DATA LOCAL INFILE '/opt/venues.csv'
INTO TABLE info
FIELDS TERMINATED BY ','
IGNORE 1 ROWS;
