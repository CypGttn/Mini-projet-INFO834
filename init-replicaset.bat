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
rmdir /s /q "%BASE_DIR%\data\r1" 2>nul
rmdir /s /q "%BASE_DIR%\data\r2" 2>nul
rmdir /s /q "%BASE_DIR%\data\r3" 2>nul

mkdir "%BASE_DIR%\data\r1" 2>nul
mkdir "%BASE_DIR%\data\r2" 2>nul
mkdir "%BASE_DIR%\data\r3" 2>nul

echo -------------------------------------
echo Lancement des instances MongoDB...
echo -------------------------------------
start /min "MongoDB1" cmd /k mongod --replSet rs0 --port %MONGO_PORT1% --dbpath "%BASE_DIR%\data\r1" --bind_ip localhost --oplogSize 128
start /min "MongoDB2" cmd /k mongod --replSet rs0 --port %MONGO_PORT2% --dbpath "%BASE_DIR%\data\r2" --bind_ip localhost --oplogSize 128
start /min "MongoDB3" cmd /k mongod --replSet rs0 --port %MONGO_PORT3% --dbpath "%BASE_DIR%\data\r3" --bind_ip localhost --oplogSize 128

timeout /t 30 >nul

echo Vérification de l'état des instances MongoDB...

:waitForPorts
echo Tentative de connexion aux ports %MONGO_PORT1%, %MONGO_PORT2%, %MONGO_PORT3%...
mongosh --quiet --port %MONGO_PORT1% --eval "db.runCommand({ ping: 1 })" >nul 2>&1
set PORT1_OK=%ERRORLEVEL%
mongosh --quiet --port %MONGO_PORT2% --eval "db.runCommand({ ping: 1 })" >nul 2>&1
set PORT2_OK=%ERRORLEVEL%
mongosh --quiet --port %MONGO_PORT3% --eval "db.runCommand({ ping: 1 })" >nul 2>&1
set PORT3_OK=%ERRORLEVEL%

if NOT "%PORT1_OK%"=="0" (
    echo Port %MONGO_PORT1% pas encore prêt
)
if NOT "%PORT2_OK%"=="0" (
    echo Port %MONGO_PORT2% pas encore prêt
)
if NOT "%PORT3_OK%"=="0" (
    echo Port %MONGO_PORT3% pas encore prêt
)

if NOT "%PORT1_OK%"=="0" (
    timeout /t 2 >nul
    goto waitForPorts
)
if NOT "%PORT2_OK%"=="0" (
    timeout /t 2 >nul
    goto waitForPorts
)
if NOT "%PORT3_OK%"=="0" (
    timeout /t 2 >nul
    goto waitForPorts
)

echo Tous les ports MongoDB sont prêts.


echo -------------------------------------
echo Initialisation du Replica Set...
echo -------------------------------------

:: Crée correctement le fichier init_rs.js avec redirection
echo rs.initiate({_id: "rs0", members: [^{_id: 0, host: "localhost:%MONGO_PORT1%"^}, ^{_id: 1, host: "localhost:%MONGO_PORT2%"^}, ^{_id: 2, host: "localhost:%MONGO_PORT3%"^}]}); > init_rs.js

echo Contenu de init_rs.js :
type init_rs.js


:: Exécute le script dans mongosh
echo Exécution de rs.initiate()...
mongosh --port %MONGO_PORT1% < init_rs.js


:: Vérifie si le Replica Set est bien initialisé après un délai
timeout /t 20 >nul
echo Vérification du Replica Set...
mongosh --port %MONGO_PORT1% --eval "rs.status()"

echo -------------------------------------
echo ✔ Replica Set initialisé
echo -------------------------------------

:: Supprimer le fichier temporaire
del /f /q init_rs.js

endlocal
pause
