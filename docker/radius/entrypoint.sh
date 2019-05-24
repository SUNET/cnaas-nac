echo ">> Waiting for postgres to start"
WAIT=0
while ! nc -z nac_postgres 5432; do
    sleep 1
    WAIT=$(($WAIT + 1))
      if [ "$WAIT" -gt 15 ]; then
          echo "Error: Timeout wating for Postgres to start"
          exit 1
      fi
done

psql -h nac_postgres -U cnaas nac -f /tmp/schema.sql
ln -s /etc/freeradius/3.0/mods-available/sql /etc/freeradius/3.0/mods-enabled
freeradius -X -f
