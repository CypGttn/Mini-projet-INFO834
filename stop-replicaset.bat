@echo off
echo -------------------------------------
echo Arrêt des instances MongoDB...
echo -------------------------------------

:: Ferme les fenêtres "MongoDB1", "MongoDB2", "MongoDB3"
taskkill /FI "WINDOWTITLE eq MongoDB1" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq MongoDB2" /F >nul 2>&1
taskkill /FI "WINDOWTITLE eq MongoDB3" /F >nul 2>&1

echo ✔ Tous les serveurs ont été arrêtés.

pause
