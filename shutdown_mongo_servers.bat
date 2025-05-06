@echo off
setlocal

:: CONFIG
set BASE_DIR=C:\mongo-repl
set MONGO_PORT1=27017
set MONGO_PORT2=27018
set MONGO_PORT3=27019

echo -------------------------------------
echo Arrêt propre des instances MongoDB...
echo -------------------------------------

:: Tentative d'arrêt propre via mongosh
for %%P in (%MONGO_PORT1% %MONGO_PORT2% %MONGO_PORT3%) do (
    echo ➤ Tentative d'arrêt sur le port %%P...
    mongosh --quiet --port %%P --eval "db.getSiblingDB('admin').shutdownServer({timeoutSecs: 5})" >nul 2>&1
)

timeout /t 3 >nul

echo -------------------------------------
echo Vérification : fermeture forcée si nécessaire...
echo -------------------------------------

:: Fermer toutes les instances restantes de mongod
taskkill /FI "WINDOWTITLE eq MongoDB1" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq MongoDB2" /T /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq MongoDB3" /T /F >nul 2>&1

echo -------------------------------------
echo ✔ Tous les serveurs MongoDB sont arrêtés.
echo -------------------------------------
pause
