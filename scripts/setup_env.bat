@echo off
echo ========================================
echo SETUP ENVIRONNEMENT PYTHON SPIDERVISION
echo ========================================

echo.
echo 1. Suppression ancien environnement...
if exist .venv rmdir /s /q .venv

echo.
echo 2. Creation nouvel environnement virtuel...
python -m venv .venv
if errorlevel 1 (
    echo ERREUR: Python non trouve. Essai avec py...
    py -m venv .venv
    if errorlevel 1 (
        echo ERREUR: Impossible de creer l'environnement virtuel
        echo Verifiez que Python est installe
        pause
        exit /b 1
    )
)

echo.
echo 3. Activation environnement...
call .venv\Scripts\activate.bat

echo.
echo 4. Mise a jour pip...
python -m pip install --upgrade pip

echo.
echo 5. Installation des dependances...
pip install requests
pip install pandas
pip install python-dotenv
pip install click

echo.
echo 6. Verification installations...
python -c "import requests; print('✓ requests OK')"
python -c "import pandas; print('✓ pandas OK')"
python -c "import dotenv; print('✓ python-dotenv OK')"
python -c "import click; print('✓ click OK')"

echo.
echo 7. Test du script principal...
python generate_last_day_report.py

echo.
echo ========================================
echo SETUP TERMINE !
echo ========================================
pause
