@echo off
title Quick Start - Scraper Setup
echo 🚀 QUICK START - Sistema de Scraping
echo =====================================
echo.

echo 📁 Verificando ubicación...
echo Estás en: %CD%
echo.

echo 🔍 Paso 1: Verificando setup...
call check_setup.bat
if errorlevel 1 (
    echo ❌ Setup incompleto
    pause
    exit /b 1
)

echo.
echo 🚀 Paso 2: Iniciando sistema...
call run.bat
if errorlevel 1 (
    echo ❌ Error al iniciar
    pause
    exit /b 1
)

echo.
echo ✅ Sistema iniciado!
echo 📊 ¿Quieres abrir el monitor? (S/N)
set /p MONITOR="Respuesta: "
if /i "%MONITOR%"=="S" (
    start monitor.bat
)

echo.
echo 🎉 Todo listo! El scraping está ejecutándose.
echo 📁 Resultados en: %CD%\results\
pause