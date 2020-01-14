# Make sure we have a connection to Postgres
WAIT=0

while ! nc -z cnaas_postgres 5432; do
    sleep 1
    WAIT=$(($WAIT + 1))
      if [ "$WAIT" -gt 15 ]; then
          echo "Error: Timeout wating for Postgres to start"
          exit 1
      fi
done

# Create the NAC database
createdb -h cnaas_postgres -U cnaas nac

# Create tables etc from the stored schema
psql -h cnaas_postgres -U cnaas nac -f /tmp/schema.sql

if [ $? -ne 0 ]; then
    echo "Error: Failed to create tables"
    exit 1
fi

# Clone settings from repository
git clone $GITREPO_ETC /tmp/gitrepo_etc

# Move the sites-default file if it exists
if [ -f "/tmp/gitrepo_etc/radius/site-default" ]; then
    cp /tmp/gitrepo_etc/radius/site-default /etc/freeradius/3.0/sites-available/default
fi

# Copy the rest of the files
cp /tmp/gitrepo_etc/radius/* /etc/freeradius/3.0/

# Replace PSKs when needed
sed -e "s/EDUROAM_R1_SECRET/$EDUROAM_R1_SECRET/" \
    -e "s/EDUROAM_R2_SECRET/$EDUROAM_R2_SECRET/" \
  < /etc/freeradius/3.0/proxy.conf > /tmp/proxy.conf.new \
  && cat /tmp/proxy.conf.new > /etc/freeradius/3.0/proxy.conf
sed -e "s/RADIUS_SERVER_SECRET/$RADIUS_SERVER_SECRET/" \
  < /etc/freeradius/3.0/clients.conf > /tmp/clients.conf.new \
  && cat /tmp/clients.conf.new > /etc/freeradius/3.0/clients.conf

# Create symlinks
ln -s /etc/freeradius/3.0/mods-available/sql /etc/freeradius/3.0/mods-enabled

# Start freeradius in the foreground with debug enabled
freeradius -X -f
