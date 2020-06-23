# Wait a while for PostgreSQL and API to start
sleep 5

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
    -e "s/MDH_ISE_SECRET/$MDH_ISE_SECRET/" \
  < /etc/freeradius/3.0/proxy.conf > /tmp/proxy.conf.new \
  && cat /tmp/proxy.conf.new > /etc/freeradius/3.0/proxy.conf

sed -e "s/RADIUS_SERVER_SECRET/$RADIUS_SERVER_SECRET/" \
  < /etc/freeradius/3.0/clients.conf > /tmp/clients.conf.new \
  && cat /tmp/clients.conf.new > /etc/freeradius/3.0/clients.conf

sed -e "s/LDAP_SERVER/${LDAP_SERVER}/" \
    -e "s/LDAP_IDENTITY/${LDAP_IDENTITY}/" \
    -e "s/LDAP_PASSWORD/${LDAP_PASSWORD}/" \
    -e "s/LDAP_BASE_DN/${LDAP_BASE_DN}/" \
  < /etc/freeradius/3.0/mods-available/ldap > /tmp/ldap.new \
  && cat /tmp/ldap.new > /etc/freeradius/3.0/mods-available/ldap

sed -e "s/NTLM_DOMAIN/${NTLM_DOMAIN}/" \
  < /etc/freeradius/3.0/mods-available/ntlm_auth > /tmp/ntlm_auth.new \
  && cat /tmp/ntlm_auth.new > /etc/freeradius/3.0/mods-available/ntlm_auth

# Configure DNS server
if [ ${AD_DNS_PRIMARY} ]; then
    echo "nameserver ${AD_DNS_PRIMARY}" >> /etc/resolv.conf
fi

if [ ${AD_DNS_SECONDARY} ]; then
    echo "nameserver ${AD_DNS_SECONDARY}" >> /etc/resolv.conf
fi

if [ ${LDAP_SERVER} ]; then
    ping -c5 $LDAP_SERVER
fi

# Start freeradius in the foreground with debug enabled
freeradius -X
