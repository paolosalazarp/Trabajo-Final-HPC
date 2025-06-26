@echo off
echo Deteniendo sistema de scraping...
echo Ruta: %CD%

docker compose down
if errorlevel 1 (
    echo ERROR: Error al detener los servicios
    pause
    exit /b 1
)

echo EXITO: Sistema detenido correctamente
echo Los resultados estan en: %CD%\results\
pause