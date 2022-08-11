FROM debian:bullseye

ENV DEBIAN_FRONTEND noninteractive

# Create directories
RUN mkdir -p /opt/cnaas/
RUN mkdir -p /etc/cnaas-nac/src/
RUN mkdir /opt/cnaas/certs/

RUN /bin/sed -i s/deb.debian.org/ftp.se.debian.org/g /etc/apt/sources.list
RUN apt-get update && \
    apt-get -y dist-upgrade && \
    apt-get install -y \
    git \
    python3-venv \
    python3-pip \
    python3-yaml \
    iputils-ping \
    procps \
    bind9-host \
    netcat-openbsd \
    net-tools \
    curl \
    netcat \
    nginx \
    supervisor \
    libssl-dev \
    cron \
    emacs-nox \
    uwsgi-plugin-python3 \
    && apt-get clean

RUN pip3 install uwsgi
RUN python3 -m venv /opt/cnaas/venv

WORKDIR /opt/cnaas/venv/
RUN mkdir cnaas-nac

COPY . /opt/cnaas/venv/cnaas-nac/
COPY docker/api/config/db_config.yml /etc/cnaas-nac/db_config.yml
COPY docker/api/config/uwsgi_internal.ini /opt/cnaas/
COPY docker/api/config/uwsgi_external.ini /opt/cnaas/
COPY docker/api/config/supervisord_app.conf /etc/supervisor/supervisord.conf
COPY docker/api/config/nginx_internal.conf /etc/nginx/sites-available/
COPY docker/api/config/nginx_external.conf /etc/nginx/sites-available/
COPY docker/api/cert/*.pem /opt/cnaas/certs/
COPY docker/api/exec-pre-app.sh /opt/cnaas/
COPY docker/api/config/cleanup /etc/cron.daily/
COPY docker/api/config/replicate /etc/cron.daily/

RUN touch /var/log/cron.log
RUN chmod +x /etc/cron.daily/cleanup

# Install requirements
COPY setup.sh /opt/cnaas/setup.sh
COPY requirements.txt /opt/cnaas/
RUN /opt/cnaas/setup.sh

# Give nginx some special treatment
RUN unlink /etc/nginx/sites-enabled/default
RUN ln -s /etc/nginx/sites-available/nginx_internal.conf /etc/nginx/sites-enabled/nginx_internal.conf
RUN ln -s /etc/nginx/sites-available/nginx_external.conf /etc/nginx/sites-enabled/nginx_external.conf

# Expose 1443
EXPOSE 1443

ENTRYPOINT supervisord -c /etc/supervisor/supervisord.conf
