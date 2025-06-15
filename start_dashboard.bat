@echo off
echo =================================================
echo    DEMARRAGE DU TABLEAU DE BORD AMELIORE
echo =================================================
echo.

REM Vérifier si Python est disponible
where python >nul 2>&1
if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Python n'est pas disponible dans le chemin d'acces.
    echo Veuillez installer Python et l'ajouter au PATH.
    pause
    exit /b 1
)

REM Vérifier et nettoyer les données de prix
echo [INFO] Nettoyage des données de prix...
python clean_prices_data.py

REM Lancer le tableau de bord amélioré
echo.
echo [INFO] Lancement du tableau de bord...
python improved_dashboard.py

pause
