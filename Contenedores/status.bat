@echo off
echo Estado actual del sistema de scraping
echo ========================================

echo.
echo Contenedores:
docker compose ps

echo.
echo Estadisticas de Redis:
echo Ejecutando comandos Redis...

docker compose exec redis redis-cli llen player_urls >temp_queue.txt 2>nul
set /p QUEUE_SIZE=<temp_queue.txt
del temp_queue.txt 2>nul
if "%QUEUE_SIZE%"=="" set QUEUE_SIZE=0
echo   URLs en cola: %QUEUE_SIZE%

docker compose exec redis redis-cli llen scraping_results >temp_results.txt 2>nul
set /p RESULTS_COUNT=<temp_results.txt
del temp_results.txt 2>nul
if "%RESULTS_COUNT%"=="" set RESULTS_COUNT=0
echo   Resultados: %RESULTS_COUNT%

docker compose exec redis redis-cli llen scraping_errors >temp_errors.txt 2>nul
set /p ERRORS_COUNT=<temp_errors.txt
del temp_errors.txt 2>nul
if "%ERRORS_COUNT%"=="" set ERRORS_COUNT=0
echo   Errores: %ERRORS_COUNT%

echo.
echo Uso de recursos:
docker stats --no-stream --format "table {{.Container}}\t{{.CPUPerc}}\t{{.MemUsage}}" | findstr scraper

pause