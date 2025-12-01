#!/usr/bin/env bash
# exit on error
set -o errexit

pip install -r requirements.txt

python manage.py collectstatic --no-input
python manage.py migrate

echo "--- INICIANDO CONFIGURACION DE ROLES ---"
python manage.py setup_roles
echo "--- FIN CONFIGURACION DE ROLES ---"