@echo off
echo =====================================
echo Lancement complet de l'application
echo =====================================

:: 1. Vérifier si MongoDB est déjà lancé sur le port 27017
echo [1/3] Vérification du Replica Set MongoDB...

:: Test de connexion silencieuse à mongosh
mongosh --quiet --port 27017 --eval "db.runCommand({ ping: 1 })" >nul 2>&1

if %errorlevel% NEQ 0 (
    echo ➤ MongoDB Replica Set non détecté. Démarrage...
    call init-replicaset.bat
    timeout /t 5 >nul
) else (
    echo ✔ MongoDB Replica Set déjà en cours d'exécution.
)

:: Attente de l'élection du PRIMARY
echo Attente de l'élection du PRIMARY...
:waitPrimary
mongosh --quiet --port 27017 --eval "s = rs.status(); s.members && s.members.find(m => m.stateStr === 'PRIMARY') ? quit() : quit(1)" >nul 2>&1
if %errorlevel% NEQ 0 (
    echo Le PRIMARY n'est pas encore élu, nouvelle tentative...
    timeout /t 2 >nul
    goto waitPrimary
)
echo ✔ PRIMARY élu, poursuite de l'initialisation...

echo Lancement du watchdog de surveillance...
start "Mongo Watchdog" cmd /c mongo_watchdog_all.bat

:: 2. Initialisation MongoDB (drop, insert, etc.)
echo [2/3] Initialisation de la base MongoDB...
call init_mongo_with_data.bat

:: 3. Lancer l'application Python
echo [3/3] Lancement de l'application Python...
python .\app.py

echo =====================================
echo L'application est prête à être utilisée
echo =====================================

pause
