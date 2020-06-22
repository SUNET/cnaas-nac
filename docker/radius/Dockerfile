FROM debian:latest

ENV DEBIAN_FRONTEND noninteractive

# Install freeradius
RUN apt update
RUN apt install -y freeradius freeradius-postgresql freeradius-rest python3 python3-requests postgresql netcat samba winbind emacs-nox krb5-user git freeradius-ldap

WORKDIR /etc/freeradius/3.0/

# Copy to container
COPY config/ /root/config/
COPY schema.sql /tmp/
COPY entrypoint.sh /usr/local/bin/

# Copy individual files
RUN cp /root/config/dictionary .
RUN cp /root/config/mods-available/* mods-available/
RUN cp /root/config/sites-available/* sites-available/
RUN cp /root/config/mods-config/files/authorize mods-config/files/authorize

# Make symlinks
WORKDIR /etc/freeradius/3.0/mods-enabled/
RUN ln -s ../mods-available/rest rest
RUN ln -s ../mods-available/sql sql
RUN ln -s ../mods-available/ldap ldap

WORKDIR /etc/freeradius/3.0/

# Run freeradius with debug enabled
CMD sh /usr/local/bin/entrypoint.sh
