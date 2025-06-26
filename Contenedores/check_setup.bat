@echo off
title Verificacion del Setup
echo Verificando configuracion para scraping...
echo ================================================

echo Ruta actual: 
echo %CD%
echo.

echo Usuario: %USERNAME%
echo Computadora: %COMPUTERNAME%
echo Fecha: %DATE% %TIME%
echo.

echo Verificando Docker...
docker --version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no esta instalado
    goto :error
) else (
    echo OK: Docker instalado: 
    docker --version
)

docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no esta ejecutandose
    goto :error
) else (
    echo OK: Docker esta ejecutandose
)

docker compose version >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker Compose no disponible
    goto :error
) else (
    echo OK: Docker Compose disponible:
    docker compose version
)
echo.

echo Verificando archivos del proyecto...
set FILES_OK=1

if exist "docker-compose.yml" (
    echo OK: docker-compose.yml
) else (
    echo ERROR: docker-compose.yml
    set FILES_OK=0
)

if exist "Dockerfile" (
    echo OK: Dockerfile
) else (
    echo ERROR: Dockerfile
    set FILES_OK=0
)

if exist "scraper.py" (
    echo OK: scraper.py
) else (
    echo ERROR: scraper.py
    set FILES_OK=0
)

if exist "collect_results.py" (
    echo OK: collect_results.py
) else (
    echo ERROR: collect_results.py
    set FILES_OK=0
)

if exist "jugadores_sofascore.csv" (
    echo OK: jugadores_sofascore.csv
) else (
    echo ERROR: jugadores_sofascore.csv
    set FILES_OK=0
)

echo.
if %FILES_OK%==1 (
    echo EXITO: Todo esta listo para ejecutar!
    echo Ejecuta: run.bat
) else (
    echo ERROR: Faltan archivos necesarios
    goto :error
)

echo.
echo Espacio en disco:
dir | findstr "bytes free"

echo.
pause
exit /b 0

:error
echo.
echo ERROR: Hay problemas con la configuracion
echo Revisa los errores anteriores
pause
exit /b 1