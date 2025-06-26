#!/bin/bash

# Script para construir y ejecutar los contenedores

echo "🔨 Construyendo imagen Docker..."
docker build -t scraper-jugadores .

echo "📁 Creando directorios necesarios..."
mkdir -p data logs

echo "🚀 Opciones de ejecución:"
echo "1. Contenedor único: docker-compose up scraper-jugadores"
echo "2. Múltiples contenedores (paralelo): docker-compose up scraper-jugadores-1 scraper-jugadores-2 scraper-jugadores-3"
echo "3. Todos los servicios: docker-compose up"

# Hacer el script ejecutable
chmod +x build.sh