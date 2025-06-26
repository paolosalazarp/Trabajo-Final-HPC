@echo off
if "%1"=="" (
    echo Mostrando logs de todos los servicios...
    echo Presiona Ctrl+C para salir
    docker compose logs -f
) else (
    echo Mostrando logs de %1...
    echo Presiona Ctrl+C para salir
    docker compose logs -f %1
)