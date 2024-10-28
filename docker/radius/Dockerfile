FROM debian:buster

ENV DEBIAN_FRONTEND noninteractive

# Install freeradius
RUN apt-get update
RUN apt-get install -y curl gnupg2
RUN install -d -o root -g root -m 0755 /etc/apt/keyrings
RUN curl -s 'https://packages.inkbridgenetworks.com/pgp/packages.networkradius.com.asc' | tee /etc/apt/keyrings/packages.networkradius.com.asc > /dev/null
RUN echo "deb [arch=amd64 signed-by=/etc/apt/keyrings/packages.networkradius.com.asc] http://packages.networkradius.com/freeradius-3.2/debian/buster buster main" | tee /etc/apt/sources.list.d/networkradius.list > /dev/null

RUN apt-get update
RUN apt-get install -y freeradius freeradius-postgresql freeradius-rest python3 python3-requests postgresql samba winbind emacs-nox krb5-user git freeradius-ldap

# Copy to container
WORKDIR /etc/freeradius/

COPY config/ /root/config/
COPY schema.sql /tmp/
COPY entrypoint.sh /usr/local/bin/

RUN ls

RUN cp /root/config/dictionary .
RUN cp /root/config/mods-available/* mods-available/
RUN cp /root/config/sites-available/* sites-available/
RUN cp /root/config/mods-config/files/authorize mods-config/files/authorize
RUN cp /root/config/policy.d/* policy.d/

# This should be removed in the future
RUN cp /root/config/dictionary.arista /usr/share/freeradius/dictionary.arista

# Make symlinks
WORKDIR /etc/freeradius/mods-enabled/

RUN ln -s ../mods-available/rest rest
RUN ln -s ../mods-available/sql sql
RUN ln -s ../mods-available/ldap ldap

# Enable control socket
WORKDIR /etc/freeradius/sites-enabled/

RUN ln -s ../sites-available/control-socket control-socket

# Clean up packages
RUN apt clean

# Run freeradius with debug enabled
WORKDIR /etc/freeradius/
CMD sh /usr/local/bin/entrypoint.sh
