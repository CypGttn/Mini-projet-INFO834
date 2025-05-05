@echo off
echo ----------------------------
echo Initialisation de MongoDB...
echo ----------------------------

:: Démarrer mongod dans une nouvelle fenêtre, avec un vrai titre
start /min "MongoDB Server" cmd /k mongod --dbpath "C:\data\db"

:: Pause pour attendre que le serveur démarre
timeout /t 20 >nul

:: Exécuter le script d'initialisation
echo Exécution du script d'initialisation...
mongosh < "init\init_blank.js"

echo ----------------------------
echo Initialisation terminée ✔

:: Lancer le script Python
python ".\src\main.py"
