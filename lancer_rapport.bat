@echo off
REM ========================================
REM Script d'automatisation quotidienne
REM Génère le rapport SpiderVision automatiquement
REM ========================================

cd /d "%~dp0"

REM Créer le dossier logs s'il n'existe pas
if not exist "logs" mkdir logs

REM Nom du fichier log avec date et heure
set LOGFILE=logs\rapport_%date:~-4,4%%date:~-7,2%%date:~-10,2%_%time:~0,2%%time:~3,2%%time:~6,2%.log
set LOGFILE=%LOGFILE: =0%

echo ========================================= >> "%LOGFILE%" 2>&1
echo Generation rapport quotidien SpiderVision >> "%LOGFILE%" 2>&1
echo Date: %date% %time% >> "%LOGFILE%" 2>&1
echo ========================================= >> "%LOGFILE%" 2>&1
echo. >> "%LOGFILE%" 2>&1

REM Activer l'environnement virtuel
echo [INFO] Activation environnement virtuel... >> "%LOGFILE%" 2>&1
call .venv\Scripts\activate.bat >> "%LOGFILE%" 2>&1

if %ERRORLEVEL% NEQ 0 (
    echo [ERREUR] Impossible d'activer l'environnement virtuel >> "%LOGFILE%" 2>&1
    exit /b 1
)

echo [INFO] Environnement active avec succes >> "%LOGFILE%" 2>&1
echo. >> "%LOGFILE%" 2>&1

REM Générer le rapport
echo [INFO] Generation du rapport en cours... >> "%LOGFILE%" 2>&1
python generate_new_report.py >> "%LOGFILE%" 2>&1

if %ERRORLEVEL% EQU 0 (
    echo. >> "%LOGFILE%" 2>&1
    echo [SUCCES] Rapport genere avec succes ! >> "%LOGFILE%" 2>&1
    echo [SUCCES] Fichier cree dans reports/ >> "%LOGFILE%" 2>&1
) else (
    echo. >> "%LOGFILE%" 2>&1
    echo [ERREUR] Erreur lors de la generation du rapport >> "%LOGFILE%" 2>&1
    echo [ERREUR] Code erreur: %ERRORLEVEL% >> "%LOGFILE%" 2>&1
)

echo. >> "%LOGFILE%" 2>&1
echo ========================================= >> "%LOGFILE%" 2>&1
echo Fin du script - %date% %time% >> "%LOGFILE%" 2>&1
echo ========================================= >> "%LOGFILE%" 2>&1

REM Desactiver l'environnement virtuel
call .venv\Scripts\deactivate.bat >> "%LOGFILE%" 2>&1

exit /b %ERRORLEVEL%
