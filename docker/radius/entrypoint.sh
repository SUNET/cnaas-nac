echo ">> Waiting for postgres to start"
WAIT=0
while ! nc -z cnaas_postgres 5432; do
    sleep 1
    WAIT=$(($WAIT + 1))
      if [ "$WAIT" -gt 15 ]; then
          echo "Error: Timeout wating for Postgres to start"
          exit 1
      fi
done

createdb -h cnaas_postgres -U cnaas nac
if [ $? -ne 0 ]; then
    echo "Error: Failed to create database"
    exit 1
fi

psql -h cnaas_postgres -U cnaas nac -f /tmp/schema.sql
if [ $? -ne 0 ]; then
    echo "Error: Failed to create tables"
    exit 1
fi

ln -s /etc/freeradius/3.0/mods-available/sql /etc/freeradius/3.0/mods-enabled
freeradius -X -f
