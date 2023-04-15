FROM mysql:8.0.32

COPY ./venues.csv /opt/venues.csv
COPY ./load.sql /opt/load.sql
COPY ./init-venues.sql /docker-entrypoint-initdb.d/init-venues.sql
