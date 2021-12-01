cd /opt/cnaas/venv
. bin/activate

if [ ! -f /opt/cnaas/certs/nginx_cert.pem ]; then
  echo "WARNING: No cert found, using snakeoil (self-signed) certificate and key."
  cp /opt/cnaas/certs/snakeoil_cert.pem /opt/cnaas/certs/nginx_cert.pem
  cp /opt/cnaas/certs/snakeoil_key.pem /opt/cnaas/certs/nginx_key.pem
fi

(cd /opt/cnaas/venv/cnaas-nac/; alembic upgrade head)
if [ $? -ne 0 ]; then
    echo "Error: Failed to run Alembic."
    exit 1
fi

if [ $NAC_REPLICATE_USERNAME ]; then
    echo "export NAC_REPLICATE_USERNAME=$NAC_REPLICATE_USERNAME" > /root/.replication.sh
fi

if [ $NAC_REPLICATE_PASSWORD ]; then
    echo "export NAC_REPLICATE_PASSWORD=$NAC_REPLICATE_PASSWORD" >> /root/.replication.sh
fi

if [ $NAC_REPLICATE_SOURCE ]; then
    echo "export NAC_REPLICATE_SOURCE=$NAC_REPLICATE_SOURCE" >> /root/.replication.sh
fi

if [ $NAC_REPLICATE_TARGET ]; then
    echo "export NAC_REPLICATE_TARGET=$NAC_REPLICATE_TARGET" >> /root/.replication.sh
fi
