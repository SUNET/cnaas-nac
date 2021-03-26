cd /opt/cnaas/venv
. bin/activate

if [ ! -f /opt/cnaas/cert/cert.pem ]; then
  echo "WARNING: No cert found, using snakeoil (self-signed) certificate and key."
  cp /opt/cnaas/certs/snakeoil_cert.pem /opt/cnaas/certs/nginx_cert.pem
  cp /opt/cnaas/certs/snakeoil_key.pem /opt/cnaas/certs/nginx_key.pem
fi

(cd /opt/cnaas/venv/cnaas-nac/; alembic upgrade head)
if [ $? -ne 0 ]; then
    echo "Error: Failed to run Alembic."
    exit 1
fi
