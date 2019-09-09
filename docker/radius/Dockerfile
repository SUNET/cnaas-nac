FROM debian:buster

ENV DEBIAN_FRONTEND noninteractive

# Install freeradius
RUN apt update
RUN apt install -y freeradius freeradius-postgresql freeradius-rest python3 python3-requests postgresql netcat

WORKDIR /etc/freeradius/3.0/

# Copy to container
COPY config/ /root/config/
COPY schema.sql /tmp/
COPY entrypoint.sh /usr/local/bin/

# Copy individual files
RUN cp /root/config/clients.conf .
RUN cp /root/config/mods-available/* mods-available/
RUN cp /root/config/sites-available/* sites-available/
RUN cp /root/config/mods-config/files/authorize mods-config/files/authorize

# Make symlinks
RUN ln -s mods-available/rest mods-enabled/rest
RUN chown freerad:freerad mods-enabled/*

# Run freeradius with debug enabled
CMD sh /usr/local/bin/entrypoint.sh
