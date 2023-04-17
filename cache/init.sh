# Run MySQL commands to enable the `LOAD DATA LOCAL INFILE` statement and load data from a file into the `venues` database.
# Set the `local_infile` system variable to 1 to enable the `LOAD DATA LOCAL INFILE` statement.
# Execute the `load.sql` script, which contains the MySQL `LOAD DATA LOCAL INFILE` statement to load data from a file into the `venues` database.
mysql --host=cache --port=3306 --user=root --password=localpassword --database=venues -e "SET GLOBAL local_infile=1" && \
mysql --host=cache --port=3306 --user=root --password=localpassword --database=venues --local-infile < /opt/load.sql
