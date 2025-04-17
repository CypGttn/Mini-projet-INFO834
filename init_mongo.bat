@echo off
echo ----------------------------
echo Initialisation de MongoDB...
echo ----------------------------

:: Démarrer mongod (si tu veux le lancer dans ce script, sinon commente cette ligne)
start mongod --dbpath C:\data\db

:: Pause pour s'assurer que mongod est bien lancé
timeout /t 10 >nul

:: Exécution du script init.js
echo Exécution du script d'initialisation...
mongosh < init.js

echo ----------------------------
echo Initialisation terminée ✔
pause
