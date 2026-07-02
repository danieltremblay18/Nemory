#!/bin/bash
# Déploiement Nemory sur PythonAnywhere.
# Usage (dans une console Bash PythonAnywhere) :  bash ~/Nemory/deploy.sh
set -e

REPO=~/Nemory
WSGI=/var/www/danieltremblay18_pythonanywhere_com_wsgi.py

cd "$REPO"

echo "==> git pull"
git pull

# Décommente ces 2 lignes si requirements.txt a changé :
# source ~/.venvs/nemory/bin/activate
# pip install -r requirements.txt

echo "==> migrations DB"
~/.venvs/nemory/bin/flask --app wsgi init-db

echo "==> reload de l'app"
touch "$WSGI"

echo "✓ Déployé et rechargé."
