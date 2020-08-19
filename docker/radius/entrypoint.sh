# Wait a while for PostgreSQL and API to start
sleep 5

# Clone settings from repository
if [ -d "/tmp/gitrepo_etc" ]; then
    (cd /tmp/gitreport_etc; git pull)
else
    git clone $GITREPO_ETC /tmp/gitrepo_etc
fi

# Copy radiusd configuration
if [ -f "/tmp/gitrepo_etc/radius/radiusd.conf" ]; then
    cp /tmp/gitrepo_etc/radius/radiusd.conf /etc/freeradius/3.0/
fi

# Copy Samba configuration
if [ -f "/tmp/gitrepo_etc/radius/smb.conf" ]; then
    cp /tmp/gitrepo_etc/radius/smb.conf /etc/samba/
fi

# Copy Kerberos 5 configuration
if [ -f "/tmp/gitrepo_etc/radius/krb5.conf" ]; then
    cp /tmp/gitrepo_etc/radius/krb5.conf /etc/
fi

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

sed -e "s/AD_SERVER/${AD_SERVER}/" \
    -e "s/AD_USERNAME/${AD_USERNAME}/" \
    -e "s/AD_DOMAIN/${AD_DOMAIN}/" \
    -e "s/AD_PASSWORD/${AD_PASSWORD}/" \
    -e "s/AD_BASE_DN/${AD_BASE_DN}/" \
  < /etc/freeradius/3.0/mods-available/ldap > /tmp/ldap.new \
  && cat /tmp/ldap.new > /etc/freeradius/3.0/mods-available/ldap

sed -e "s/AD_DOMAIN/${AD_DOMAIN}/" \
  < /etc/freeradius/3.0/mods-available/ntlm_auth > /tmp/ntlm_auth.new \
  && cat /tmp/ntlm_auth.new > /etc/freeradius/3.0/mods-available/ntlm_auth

# Configure DNS server
if [ ${AD_DNS_PRIMARY} ]; then
    echo "nameserver ${AD_DNS_PRIMARY}" > /etc/resolv.conf
    if [ ${AD_DNS_SECONDARY} ]; then
	echo "nameserver ${AD_DNS_SECONDARY}" >> /etc/resolv.conf
    fi

    echo "nameserver 127.0.0.11" >> /etc/resolv.conf
    echo "options ndots:0" >> /etc/resolv.conf
fi

# Fix some winbind permissions
usermod -a -G winbindd_priv freerad
chown root:winbindd_priv /var/lib/samba/winbindd_privileged/

# Join the AD domain if we have a AD password configured
if [ ${AD_PASSWORD} ]; then
    net ads join -U "${AD_USERNAME}"%"${AD_PASSWORD}"
    winbindd
    wbinfo -p

    if [ $? != 0 ]; then
	echo "Failed to join AD domain, exiting."
	exit
    fi
fi

# Create directory for the socket
mkdir /var/run/freeradius/
chown freerad:freerad /var/run/freeradius

# Start freeradius in the foreground with debug enabled
freeradius -f -x -l stdout
