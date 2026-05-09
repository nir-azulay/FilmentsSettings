#!/bin/bash
cd /share/Container/FilmentsManagement

echo "Building backend image..."
docker build -t filaments-backend:latest ./backend

echo ""
echo "Building frontend image..."
docker build -t filaments-frontend:latest ./frontend

echo ""
echo "Done! Images built. Now create the application in Container Station."
echo "Or run: docker compose up -d"
