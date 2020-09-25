FROM debian:latest

ENV DEBIAN_FRONTEND noninteractive

# Install freeradius
RUN apt update
RUN apt install -y freeradius freeradius-postgresql freeradius-rest python3 python3-requests postgresql netcat samba winbind emacs-nox krb5-user git freeradius-ldap


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

# Make symlinks
WORKDIR /etc/freeradius/3.0/mods-enabled/

RUN ln -s ../mods-available/rest rest
RUN ln -s ../mods-available/sql sql
RUN ln -s ../mods-available/ldap ldap

# Enable control socket
WORKDIR /etc/freeradius/3.0/sites-enabled/

RUN ln -s ../sites-available/control-socket control-socket

# Build eapol_test
WORKDIR /tmp/

RUN apt install -y make gcc wget pkg-config libssl-dev libdbus-1-dev libnl-3-dev libnl-genl-3-dev
RUN wget http://w1.fi/releases/wpa_supplicant-2.9.tar.gz -O wpa_supplicant.tar.gz
RUN tar xzf wpa_supplicant.tar.gz

WORKDIR wpa_supplicant-2.9/wpa_supplicant

RUN cp defconfig .config
RUN sed -i 's/#CONFIG_EAPOL_TEST=y/CONFIG_EAPOL_TEST=y/' .config
RUN make eapol_test
RUN cp eapol_test /usr/local/bin/

WORKDIR /tmp/

RUN rm -rf wpa_supplicant-2.9*

# Clean up packages
RUN apt clean

# Run freeradius with debug enabled
WORKDIR /etc/freeradius/3.0/
CMD sh /usr/local/bin/entrypoint.sh
