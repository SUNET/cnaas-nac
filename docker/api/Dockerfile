FROM debian:buster

# Create directories
RUN mkdir -p /opt/cnaas
RUN mkdir /etc/cnaas-nac

# Setup script
COPY cnaas-setup.sh /opt/cnaas/cnaas-setup.sh
RUN /opt/cnaas/cnaas-setup.sh

# Start venv
RUN python3 -m venv /opt/cnaas/venv
WORKDIR /opt/cnaas/venv/
RUN sh ./bin/activate

RUN mkdir /opt/cnaas/certs/

COPY config/db_config.yml /etc/cnaas-nac/db_config.yml
COPY config/uwsgi_internal.ini /opt/cnaas/
COPY config/uwsgi_external.ini /opt/cnaas/
COPY config/supervisord_app.conf /etc/supervisor/conf.d
COPY config/nginx_internal.conf /etc/nginx/sites-available/
COPY config/nginx_external.conf /etc/nginx/sites-available/
COPY cert/*.key /etc/nginx/conf.d/
COPY cert/*.crt /etc/nginx/conf.d/
COPY cert/jwt_pubkey.pem /opt/cnaas/certs/
COPY exec-pre-app.sh /opt/cnaas/
COPY config/cleanup.cron /etc/cron.d/
COPY config/replicate.cron /etc/cron.d/

# Install cron jobs
RUN chmod 0644 /etc/cron.d/cleanup.cron
RUN chmod 0644 /etc/cron.d/replicate.cron

RUN crontab /etc/cron.d/cleanup.cron
RUN crontab /etc/cron.d/replicate.cron

RUN touch /var/log/cron.log

# Give nginx some special treatment
RUN unlink /etc/nginx/sites-enabled/default
RUN ln -s /etc/nginx/sites-available/nginx_internal.conf /etc/nginx/sites-enabled/nginx_internal.conf
RUN ln -s /etc/nginx/sites-available/nginx_external.conf /etc/nginx/sites-enabled/nginx_external.conf

# Expose 1443
EXPOSE 1443

ENTRYPOINT "supervisord"
