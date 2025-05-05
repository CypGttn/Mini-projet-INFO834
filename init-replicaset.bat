@echo off
setlocal

:: CONFIG
set BASE_DIR=C:\mongo-repl
set MONGO_PORT1=27017
set MONGO_PORT2=27018
set MONGO_PORT3=27019

echo -------------------------------------
echo Création des dossiers de données...
echo -------------------------------------
mkdir "%BASE_DIR%\data\r1" 2>nul
mkdir "%BASE_DIR%\data\r2" 2>nul
mkdir "%BASE_DIR%\data\r3" 2>nul

echo -------------------------------------
echo Lancement des instances MongoDB...
echo -------------------------------------
start /min "MongoDB1" cmd /k mongod --replSet rs0 --port %MONGO_PORT1% --dbpath "%BASE_DIR%\data\r1" --bind_ip localhost --oplogSize 128
start /min "MongoDB2" cmd /k mongod --replSet rs0 --port %MONGO_PORT2% --dbpath "%BASE_DIR%\data\r2" --bind_ip localhost --oplogSize 128
start /min "MongoDB3" cmd /k mongod --replSet rs0 --port %MONGO_PORT3% --dbpath "%BASE_DIR%\data\r3" --bind_ip localhost --oplogSize 128

timeout /t 10 >nul

echo -------------------------------------
echo Initialisation du Replica Set...
echo -------------------------------------

:: Crée correctement le fichier init_rs.js avec redirection
> init_rs.js (
    echo rs.initiate({
    echo.  _id: "rs0",
    echo.  members: [
    echo.    { _id: 0, host: "localhost:%MONGO_PORT1%" },
    echo.    { _id: 1, host: "localhost:%MONGO_PORT2%" },
    echo.    { _id: 2, host: "localhost:%MONGO_PORT3%" }
    echo.  ]
    echo });
)

:: Exécute le script dans mongosh
mongosh --port %MONGO_PORT1% < init_rs.js

echo -------------------------------------
echo ✔ Replica Set initialisé
echo -------------------------------------

:: Supprimer le fichier temporaire
del /f /q init_rs.js

endlocal
pause
