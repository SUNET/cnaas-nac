FROM debian:buster

ENV DEBIAN_FRONTEND noninteractive

# Install FreeRADIUS
RUN apt update
RUN apt dist-upgrade -y
RUN apt install -y gnupg ca-certificates
RUN echo "deb https://packages.networkradius.com/releases/debian-buster buster main" >> /etc/apt/sources.list
RUN apt-key adv --keyserver keys.gnupg.net --recv-key 0x41382202
RUN apt-get update
RUN apt-get install -y freeradius freeradius-postgresql freeradius-rest python3 python3-requests postgresql netcat samba winbind emacs-nox krb5-user git freeradius-ldap

# Copy to container
WORKDIR /etc/freeradius/3.0/
COPY config/ /root/config/
COPY schema.sql /tmp/
COPY entrypoint.sh /usr/local/bin/
COPY config/dictionary .
COPY config/sites-available/* sites-available/
COPY config/mods-config/files/authorize mods-config/files/authorize
COPY config/policy.d/* policy.d/
COPY config/mods-available/* /etc/freeradius/3.0/mods-available/
COPY config/dictionary.arista /usr/share/freeradius/dictionary.arista

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
RUN apt autoremove -y

# Run freeradius with debug enabled
WORKDIR /etc/freeradius/3.0/
CMD sh /usr/local/bin/entrypoint.sh
