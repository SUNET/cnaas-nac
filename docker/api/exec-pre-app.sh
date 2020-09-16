cd /opt/cnaas/venv
. bin/activate

(cd /opt/cnaas/venv/cnaas-nac/; alembic upgrade head)
if [ $? -ne 0 ]; then
    echo "Error: Failed to run Alembic"
    exit 1
fi
