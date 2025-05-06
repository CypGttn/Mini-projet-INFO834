@echo off
setlocal ENABLEDELAYEDEXPANSION

:: Configuration
set BASE_DIR=C:\mongo-repl\data
set REPL_NAME=rs0
set LOG_FILE=C:\mongo-repl\watchdog.log

:: Ports MongoDB à surveiller
set PORTS=27017 27018 27019

echo [%date% %time%] ▶ Surveillance MongoDB lancée >> %LOG_FILE%

:: Boucle de surveillance infinie
:CHECK_LOOP
for %%P in (%PORTS%) do (
    set "PORT=%%P"
    
    :: Déduire le répertoire en fonction du port
    if "!PORT!"=="27017" set "DIR=r1"
    if "!PORT!"=="27018" set "DIR=r2"
    if "!PORT!"=="27019" set "DIR=r3"
    
    :: Vérifie si MongoDB écoute sur ce port
    netstat -ano | findstr :!PORT! | findstr LISTENING >nul
    if errorlevel 1 (
        echo [%date% %time%] [!] MongoDB sur !PORT! inactif. Redémarrage... >> %LOG_FILE%
        start "MongoDB !PORT!" cmd /k mongod --replSet %REPL_NAME% --port !PORT! --dbpath "%BASE_DIR%\!DIR!" --bind_ip localhost --oplogSize 128
    )
)

:: Attendre 10 secondes avant de revérifier
timeout /t 10 >nul
goto CHECK_LOOP
