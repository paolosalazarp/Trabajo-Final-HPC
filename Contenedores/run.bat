@echo off
echo Iniciando sistema de scraping distribuido...
echo Ruta actual: %CD%

REM Verificar si estamos en la ruta correcta
if not exist "%CD%\docker-compose.yml" (
    echo ERROR: No se encuentra docker-compose.yml en esta ruta
    echo Asegurate de estar en: C:\Users\pc.salazarp\Desktop\xd\Trabajo-Final-HPC\Contenedores
    pause
    exit /b 1
)

REM Verificar si Docker está ejecutándose
docker info >nul 2>&1
if errorlevel 1 (
    echo ERROR: Docker no esta ejecutandose. Por favor inicia Docker Desktop.
    pause
    exit /b 1
)

REM Crear directorio de resultados
if not exist "results" mkdir "results"

REM Verificar archivos necesarios
echo Verificando archivos necesarios...
if not exist "jugadores_sofascore.csv" (
    echo ERROR: Falta jugadores_sofascore.csv
    pause
    exit /b 1
)
echo OK: jugadores_sofascore.csv encontrado

if not exist "Dockerfile" (
    echo ERROR: Falta Dockerfile
    pause
    exit /b 1
)
echo OK: Dockerfile encontrado

if not exist "scraper.py" (
    echo ERROR: Falta scraper.py
    pause
    exit /b 1
)
echo OK: scraper.py encontrado

REM Limpiar contenedores anteriores si existen
echo Limpiando contenedores anteriores...
docker compose down >nul 2>&1

REM Construir las imágenes
echo Construyendo imagenes Docker...
docker compose build --no-cache

if errorlevel 1 (
    echo ERROR: Error al construir las imagenes
    pause
    exit /b 1
)

REM Iniciar los servicios
echo Iniciando servicios...
docker compose up -d

if errorlevel 1 (
    echo ERROR: Error al iniciar los servicios
    pause
    exit /b 1
)

echo EXITO: Sistema iniciado correctamente!
echo.
echo Comandos utiles:
echo   Ver logs: docker compose logs -f
echo   Ver estado: docker compose ps
echo   Detener: docker compose down
echo   Monitor: monitor.bat
echo.
echo Los resultados se guardaran en: %CD%\results\
pause