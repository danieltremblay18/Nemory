"""WSGI entry point.

Development:   flask --app wsgi run --debug
Production:    waitress-serve --port=8000 wsgi:app
"""

from app import create_app

app = create_app()
