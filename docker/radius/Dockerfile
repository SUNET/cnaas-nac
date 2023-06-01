FROM debian:bullseye

ENV DEBIAN_FRONTEND noninteractive

# Install freeradius
RUN apt-get update
RUN apt-get install -y freeradius freeradius-postgresql freeradius-rest python3 python3-requests postgresql netcat-openbsd samba winbind emacs-nox krb5-user git freeradius-ldap

# Copy to container
WORKDIR /etc/freeradius/3.0/

COPY config/ /root/config/
COPY schema.sql /tmp/
COPY entrypoint.sh /usr/local/bin/

RUN cp /root/config/dictionary .
RUN cp /root/config/mods-available/* mods-available/
RUN cp /root/config/sites-available/* sites-available/
RUN cp /root/config/mods-config/files/authorize mods-config/files/authorize
RUN cp /root/config/policy.d/* policy.d/

# This should be removed in the future
RUN cp /root/config/dictionary.arista /usr/share/freeradius/dictionary.arista

# Make symlinks
WORKDIR /etc/freeradius/3.0/mods-enabled/

RUN ln -s ../mods-available/rest rest
RUN ln -s ../mods-available/sql sql
RUN ln -s ../mods-available/ldap ldap

# Enable control socket
WORKDIR /etc/freeradius/3.0/sites-enabled/

RUN ln -s ../sites-available/control-socket control-socket

# Clean up packages
RUN apt clean

# Run freeradius with debug enabled
WORKDIR /etc/freeradius/3.0/
CMD sh /usr/local/bin/entrypoint.sh
