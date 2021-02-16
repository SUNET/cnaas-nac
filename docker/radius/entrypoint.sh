
#!/bin/sh


# Wait a while for PostgreSQL and API to start
echo "[entrypoint.sh] Waiting for API and Postgres to start..."
sleep 5

# Clone settings from repository
if [ -d "/tmp/gitrepo_etc" ]; then
    (cd /tmp/gitrepo_etc; git pull)
    echo "[entrypoint.sh] Updated existing Git repository"
else
    git clone $GITREPO_ETC /tmp/gitrepo_etc
    echo "[entrypoint.sh] Cloned Git repository from $GITREPO_ETC"
fi

# Copy radiusd configuration
if [ -f "/tmp/gitrepo_etc/radius/radiusd.conf" ]; then
    cp /tmp/gitrepo_etc/radius/radiusd.conf /etc/freeradius/3.0/
    echo "[entrypoint.sh] Copied radiusd.conf"
fi

# Copy Samba configuration
if [ -f "/tmp/gitrepo_etc/radius/smb.conf" ]; then
    cp /tmp/gitrepo_etc/radius/smb.conf /etc/samba/
    echo "[entrypoint.sh] Copied smb.conf"
fi

# Copy Kerberos 5 configuration
if [ -f "/tmp/gitrepo_etc/radius/krb5.conf" ]; then
    cp /tmp/gitrepo_etc/radius/krb5.conf /etc/
    echo "[entrypoint.sh] Copied krb5.conf"
fi

# Move the sites-default file if it exists
#if [ -f "/tmp/gitrepo_etc/radius/site-default" ]; then
#    cp /tmp/gitrepo_etc/radius/site-default /etc/freeradius/3.0/sites-available/default
#    echo "[entrypoint.sh] Copied site-default"
#fi

# Copy the rest of the files
cp /tmp/gitrepo_etc/radius/* /etc/freeradius/3.0/
echo "[entrypoint.sh] Copied FreeRADIUS files"

if [ ! -z "$EDUROAM_R1_SECRET" ] && [ ! -z "$EDUROAM_R2_SECRET" ] && \
       [ ! -z "$MDH_ISE_SECRET" ]; then
    # Replace PSKs when needed
    echo "[entrypoint.sh] Setting Eduroam secrets"

    sed -e "s/EDUROAM_R1_SECRET/$EDUROAM_R1_SECRET/" \
	-e "s/EDUROAM_R2_SECRET/$EDUROAM_R2_SECRET/" \
	-e "s/MDH_ISE_SECRET/$MDH_ISE_SECRET/" \
	< /etc/freeradius/3.0/proxy.conf > /tmp/proxy.conf.new \
	&& cat /tmp/proxy.conf.new > /etc/freeradius/3.0/proxy.conf
fi

if [ ! -z "$RADIUS_SERVER_SECRET" ]; then
    echo "[entrypoint.sh] Setting RADIUS secret"

    sed -e "s/RADIUS_SERVER_SECRET/$RADIUS_SERVER_SECRET/" \
	< /etc/freeradius/3.0/clients.conf > /tmp/clients.conf.new \
	&& cat /tmp/clients.conf.new > /etc/freeradius/3.0/clients.conf
fi

if [ ! -z "$AD_USERNAME" ] && [ ! -z "$AD_PASSWORD" ] && \
       [ ! -z "$AD_DOMAIN" ] && \
       [ ! -z "$AD_BASE_DN" ] && [ "$DISABLE_AD" != "True" ]; then
    echo "[entrypoint.sh] Setting AD server and credentials"

    if [ ! -f "/etc/freeradius/3.0/mods-enabled/ldap" ]; then
	echo "[entrypoint.sh] Enabling LDAP"
	ln -s /etc/freeradius/3.0/mods-available/ldap /etc/freeradius/3.0/mods-enabled/ldap
    fi

    sed -e "s/AD_USERNAME/${AD_USERNAME}/" \
	-e "s/AD_DOMAIN/${AD_DOMAIN}/" \
	-e "s/AD_PASSWORD/${AD_PASSWORD}/" \
	-e "s/AD_BASE_DN/${AD_BASE_DN}/" \
	< /etc/freeradius/3.0/mods-available/ldap > /tmp/ldap.new \
	&& cat /tmp/ldap.new > /etc/freeradius/3.0/mods-available/ldap

    sed -e "s/AD_DOMAIN/${AD_DOMAIN}/" \
	< /etc/freeradius/3.0/mods-available/ntlm_auth > /tmp/ntlm_auth.new \
	&& cat /tmp/ntlm_auth.new > /etc/freeradius/3.0/mods-available/ntlm_auth
else
    if [ -f "/etc/freeradius/3.0/mods-enabled/ldap" ]; then
	echo "[entrypoint.sh] Disabling LDAP"
	unlink /etc/freeradius/3.0/mods-enabled/ldap
    fi

fi

# Configure DNS server
if [ ${AD_DNS_PRIMARY} ] && [ "$DISABLE_AD" != "True" ]; then
    echo "nameserver ${AD_DNS_PRIMARY}" > /etc/resolv.conf
    if [ ${AD_DNS_SECONDARY} ]; then
	echo "nameserver ${AD_DNS_SECONDARY}" >> /etc/resolv.conf
    fi

    echo "[entrypoint.sh] Configured resolvers"
fi

# Join the AD domain if we have a AD password configured
if [ ${AD_PASSWORD} ] && [ "$DISABLE_AD" != "True" ]; then
    # Test if we already joined the domain
    winbindd
    wbinfo -p

    if [ $? != 0 ]; then
	# Not joined, join it
	killall winbindd

	# Fix some winbind permissions
	usermod -a -G winbindd_priv freerad
	chown root:winbindd_priv /var/lib/samba/winbindd_privileged/

	# Join the AD domain
	net ads join -U "${AD_USERNAME}"%"${AD_PASSWORD}"
	if [ $? != 0 ]; then
	    echo "Failed to join AD domain, exiting."
	    exit
	else
	    echo "[entrypoint.sh] Joined AD domain"
	fi

	winbindd
	wbinfo -p

	if [ $? != 0 ]; then
	    echo "Could not start windbindd, exiting."
	    exit
	else
	    echo "[entrypoint.sh] Started windbindd"
	fi
    fi

    chgrp freerad /var/lib/samba/winbindd_privileged/
fi

# Create directory for the socket
if [ ! -d /var/run/freeradius/ ]; then
    mkdir /var/run/freeradius/
fi

chown freerad:freerad /var/run/freeradius

# Start freeradius in the foreground with debug enabled
freeradius -f -x -l stdout
