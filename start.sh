#!/bin/bash

# Define o app Flask
export FLASK_APP=app.py
export FLASK_ENV=production

# Se PORT não estiver definido, usa 8080
PORT=${PORT:-8080}

# Se estiver em produção, usar Gunicorn
if [ "$RAILPACK_ENV" = "production" ]; then
    echo "Starting with Gunicorn..."
    exec gunicorn -w 4 -b 0.0.0.0:$PORT app:app
else
    echo "Starting with Flask dev server..."
    exec python3 -m flask run --host=0.0.0.0 --port=$PORT
fi
