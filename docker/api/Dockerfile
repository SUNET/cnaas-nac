FROM debian:buster

# Install package dependencies
RUN apt update
RUN apt install -y python3 python3-pip git python3-venv python3-yaml netcat \
	nginx supervisor
RUN pip3 install uwsgi

# Create directories
RUN mkdir -p /opt/cnaas
RUN mkdir /etc/cnaas-nac

# Start venv
RUN python3 -m venv /opt/cnaas/venv
WORKDIR /opt/cnaas/venv/
RUN sh ./bin/activate

# Fetch the code
RUN git clone https://github.com/SUNET/cnaas-nac.git
WORKDIR /opt/cnaas/venv/cnaas-nac/
RUN git checkout -b feature.port_locking origin/feature.port_locking
RUN python3 -m pip install -r requirements.txt

COPY config/db_config.yml /etc/cnaas-nac/db_config.yml
COPY config/uwsgi.ini /opt/cnaas/venv/cnaas-nac/
COPY config/supervisord_app.conf /etc/supervisor/conf.d
COPY config/nginx_app.conf /etc/nginx/sites-available/
COPY cert/* /etc/nginx/conf.d/
COPY exec-pre-app.sh /opt/cnaas/

# Give nginx some special treatment
RUN unlink /etc/nginx/sites-enabled/default
RUN ln -s /etc/nginx/sites-available/nginx_app.conf /etc/nginx/sites-enabled/default

# Expose 1443
EXPOSE 1443

ENTRYPOINT "supervisord"
