#!/bin/sh

# Wait a while for PostgreSQL and API to start
echo "[entrypoint.sh] Waiting for API and Postgres to start..."
sleep 10

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

    # Write Samba config
    REALM=`echo "${NTLM_DOMAIN}" | tr '[:lower:]' '[:upper:]'`

    cat <<EOF > /etc/samba/smb.conf
[global]
   workgroup = ${WORKGROUP}
   security = ADS
   realm = ${REALM}
   winbind refresh tickets = yes
   vfs objects = acl_xattr
   map acl inherit = yes
   store dos attributes = yes
EOF

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
freeradius -f -l stdout
