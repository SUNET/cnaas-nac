cd /opt/cnaas/venv
. bin/activate

(cd /opt/cnaas/venv/cnaas-nac/; git checkout feature.active_directory; alembic upgrade head)
if [ $? -ne 0 ]; then
    echo "Error: Failed to run Alembic"
    exit 1
fi
