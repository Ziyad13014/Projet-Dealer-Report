@echo off
title SpiderVision Report Generator
color 0A

echo.
echo ========================================
echo   SPIDERVISION REPORT GENERATOR
echo ========================================
echo.

cd /d "%~dp0"

echo Activation environnement Python...
call .venv\Scripts\activate.bat

echo.
echo Generation du rapport en cours...
echo.

python -u lance_un_rapport.py

echo.
echo ========================================
echo Rapport genere avec succes !
echo ========================================
echo.
echo Le fichier HTML a ete cree dans le dossier reports/
echo Ouvrez-le dans votre navigateur pour voir le rapport.
echo.

pause
