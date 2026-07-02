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
~/.venvs/nemory/bin/python3 - <<'PYEOF'
import sqlite3, os
db = sqlite3.connect(os.path.join(os.path.dirname(__file__), 'instance', 'nemory.sqlite'))
cols = [
    ("assets",     "notes",    "TEXT NOT NULL DEFAULT ''"),
    ("assets",     "supplier", "TEXT NOT NULL DEFAULT ''"),
    ("assets",     "contact",  "TEXT NOT NULL DEFAULT ''"),
    ("assets",     "year",     "INTEGER"),
    ("assets",     "owner",    "TEXT NOT NULL DEFAULT ''"),
    ("activities", "cost",     "REAL"),
]
for table, col, typedef in cols:
    try:
        db.execute(f"ALTER TABLE {table} ADD COLUMN {col} {typedef}")
        print(f"  + {table}.{col}")
    except Exception:
        pass  # déjà présent
db.commit()
db.close()
PYEOF

echo "==> reload de l'app"
touch "$WSGI"

echo "✓ Déployé et rechargé."
