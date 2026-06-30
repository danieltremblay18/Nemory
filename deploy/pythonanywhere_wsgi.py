# PythonAnywhere WSGI configuration for Nemory — READY-TO-PASTE TEMPLATE.
#
# This file is NOT used automatically. PythonAnywhere serves your app through its
# own file at /var/www/danieltremblay18_pythonanywhere_com_wsgi.py. To deploy:
#   1. Web tab -> click the "WSGI configuration file" link.
#   2. Delete everything in that file.
#   3. Paste the contents below.
#   4. Fill in the two secrets (SECRET_KEY, NEMORY_PASSWORD), then Reload.
#
# This copy lives in the repo only so you have a correct reference to copy from.
# Paths use the danieltremblay18 account; change them only if you deploy elsewhere.

import os
import sys

# 1. Make the project importable. Must come BEFORE importing the app.
PROJECT_DIR = "/home/danieltremblay18/Nemory"
if PROJECT_DIR not in sys.path:
    sys.path.insert(0, PROJECT_DIR)

# 2. Secrets / config. Must be set BEFORE the import below: config.py reads these
#    from os.environ at import time.
#    Generate a key with: python -c "import secrets; print(secrets.token_hex(32))"
os.environ["NEMORY_ENV"] = "production"  # enables the secret-safety guard
os.environ["SECRET_KEY"] = "PASTE_A_GENERATED_KEY_HERE"
os.environ["NEMORY_PASSWORD"] = "CHANGE_ME"  # the password you log in with

# Optional: pin the database location. The default is <project>/instance/nemory.sqlite,
# which is already persistent on PythonAnywhere, so you usually don't need this.
# os.environ["DATABASE"] = "/home/danieltremblay18/Nemory/instance/nemory.sqlite"

# 3. Expose the Flask app under the name PythonAnywhere looks for: "application".
from wsgi import app as application
