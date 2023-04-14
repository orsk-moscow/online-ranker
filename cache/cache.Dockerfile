FROM mysql:8.0.32

ENV MYSQL_ROOT_HOST=%
ENV MYSQL_USER=localuser
ENV MYSQL_PASSWORD=localpassword
ENV MYSQL_ROOT_PASSWORD=localpassword
ENV MYSQL_DATABASE=venues

COPY ./venues.csv /opt/venues.csv
COPY ./load.sql /opt/load.sql
COPY ./init-venues.sql /docker-entrypoint-initdb.d/init-venues.sql
