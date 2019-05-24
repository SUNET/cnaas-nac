FROM debian:buster

# Install package dependencies
RUN apt update
RUN apt install -y python3 python3-pip git python3-venv python3-yaml netcat

# Create directories
RUN mkdir /cnaas
RUN mkdir -p /opt/cnaas
RUN mkdir /etc/cnaas-nac

# Start venv
RUN python3 -m venv /opt/cnaas/venv

WORKDIR /opt/cnaas/venv/

RUN sh ./bin/activate

# Fetch the code
RUN git clone https://github.com/SUNET/cnaas-nac.git

WORKDIR /opt/cnaas/venv/cnaas-nac/

RUN python3 -m pip install -r requirements.txt
COPY db_config.yml /etc/cnaas-nac/db_config.yml
COPY entrypoint.sh /usr/local/bin/

WORKDIR /opt/cnaas/venv/cnaas-nac/src/

EXPOSE 5001

CMD sh /usr/local/bin/entrypoint.sh
