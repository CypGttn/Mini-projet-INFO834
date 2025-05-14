@echo off
echo ----------------------------
echo Initialisation de MongoDB...
echo ----------------------------

:: Attendre un peu pour s'assurer que le PRIMARY est élu (si pas déjà fait)
timeout /t 5 >nul

:: Exécution du script d'initialisation sur le PRIMARY (port 27017)
echo Exécution du script d'initialisation...
mongosh --port 27017 < "init\init.js"

echo ----------------------------
echo Initialisation terminée ✔
