@echo off
title Monitor del Sistema de Scraping

:loop
cls
echo Monitor del sistema de scraping - %date% %time%
echo ==================================
echo Ubicacion: %CD%
echo.

echo Estado de contenedores:
docker compose ps 2>nul
if errorlevel 1 (
    echo ERROR: No se pueden obtener los contenedores
    echo Esta el sistema ejecutandose? Ejecuta run.bat primero
    goto :wait
)

echo.
echo Estadisticas de Redis:

REM Verificar si Redis esta ejecutandose
docker compose exec -T redis redis-cli ping >nul 2>&1
if errorlevel 1 (
    echo ERROR: Redis no esta disponible
    goto :wait
)

REM Obtener estadisticas
for /f "tokens=*" %%i in ('docker compose exec -T redis redis-cli llen player_urls 2^>nul') do set QUEUE_SIZE=%%i
if "%QUEUE_SIZE%"=="" set QUEUE_SIZE=0

for /f "tokens=*" %%i in ('docker compose exec -T redis redis-cli llen scraping_results 2^>nul') do set RESULTS_COUNT=%%i
if "%RESULTS_COUNT%"=="" set RESULTS_COUNT=0

for /f "tokens=*" %%i in ('docker compose exec -T redis redis-cli llen scraping_errors 2^>nul') do set ERRORS_COUNT=%%i
if "%ERRORS_COUNT%"=="" set ERRORS_COUNT=0

echo   URLs en cola: %QUEUE_SIZE%
echo   Resultados: %RESULTS_COUNT%
echo   Errores: %ERRORS_COUNT%

echo.
echo Uso de recursos:
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" 2>nul | findstr scraper
if errorlevel 1 (
    echo ERROR: No se pueden obtener estadisticas de recursos
)

echo.
echo Archivos de resultados:
if exist "results" (
    dir /b "results\*.csv" 2>nul
    if errorlevel 1 (
        echo   No hay archivos CSV aun
    )
) else (
    echo   Carpeta results no existe
)

:wait
echo.
echo Presiona Ctrl+C para salir o espera 15 segundos para actualizar...
timeout /t 15 /nobreak >nul
if errorlevel 1 goto :end
goto loop

:end
echo Monitor cerrado