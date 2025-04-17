@echo off
echo =====================================
echo 🚀 Lancement complet de l'application
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

:: 2. Initialisation MongoDB (drop, insert, etc.)
echo [2/3] Initialisation de la base MongoDB...
call init_mongo_blank.bat

:: 3. Lancer l'application Python
echo [3/3] Lancement de l'application Python...
python .\src\main.py

pause
