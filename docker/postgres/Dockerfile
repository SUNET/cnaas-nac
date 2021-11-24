FROM postgres:11

COPY nac.sql /docker-entrypoint-initdb.d/
COPY pg_cron.sh /docker-entrypoint-initdb.d/

RUN apt update
RUN apt install postgresql-11-cron

EXPOSE 5432
