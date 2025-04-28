#!/bin/bash

# Attendre que la base de données soit prête
echo "Waiting for database to be ready..."
until pg_isready -h ${POSTGRES_SERVER} -U ${POSTGRES_USER}; do
  sleep 1
done

# Exécuter les migrations
echo "Running database migrations..."
alembic upgrade head

# Démarrer l'application
echo "Starting application..."
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload 