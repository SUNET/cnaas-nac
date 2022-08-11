FROM debian:buster

ENV DEBIAN_FRONTEND noninteractive

# Create directories
RUN mkdir -p /opt/cnaas
RUN mkdir /etc/cnaas-nac

# Setup script
COPY cnaas-setup.sh /opt/cnaas/cnaas-setup.sh
RUN /opt/cnaas/cnaas-setup.sh

RUN mkdir /opt/cnaas/certs/

COPY config/db_config.yml /etc/cnaas-nac/db_config.yml
COPY config/uwsgi_internal.ini /opt/cnaas/
COPY config/uwsgi_external.ini /opt/cnaas/
COPY config/supervisord_app.conf /etc/supervisor/supervisord.conf
COPY config/nginx_internal.conf /etc/nginx/sites-available/
COPY config/nginx_external.conf /etc/nginx/sites-available/
COPY cert/*.pem /opt/cnaas/certs/
COPY exec-pre-app.sh /opt/cnaas/
COPY config/cleanup /etc/cron.daily/
COPY config/replicate /etc/cron.hourly/

RUN touch /var/log/cron.log
RUN chmod +x /etc/cron.daily/cleanup
RUN chmod +x /etc/cron.hourly/replicate

# Give nginx some special treatment
RUN unlink /etc/nginx/sites-enabled/default
RUN ln -s /etc/nginx/sites-available/nginx_internal.conf /etc/nginx/sites-enabled/nginx_internal.conf
RUN ln -s /etc/nginx/sites-available/nginx_external.conf /etc/nginx/sites-enabled/nginx_external.conf

# Expose 1443
EXPOSE 1443

ENTRYPOINT supervisord -c /etc/supervisor/supervisord.conf
