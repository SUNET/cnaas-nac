#!/bin/bash

set -e
set -x

export DEBIAN_FRONTEND noninteractive

/bin/sed -i s/deb.debian.org/ftp.se.debian.org/g /etc/apt/sources.list

apt-get update && \
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

pip3 install uwsgi

# Start venv
python3 -m venv /opt/cnaas/venv
cd /opt/cnaas/venv/
source bin/activate

/opt/cnaas/venv/bin/pip3 install -U pip

# Fetch the code and install dependencies
git clone https://github.com/SUNET/cnaas-nac.git
cd cnaas-nac/
/opt/cnaas/venv/bin/pip3 install -r requirements.txt

# Clean up packages
apt-get clean
