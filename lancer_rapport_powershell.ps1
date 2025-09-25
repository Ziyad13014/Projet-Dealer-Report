# SpiderVision Report Generator - PowerShell
# Double-clic pour lancer

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   SPIDERVISION REPORT GENERATOR" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Changer vers le répertoire du script
Set-Location $PSScriptRoot

Write-Host "Activation environnement Python..." -ForegroundColor Yellow
& .venv\Scripts\Activate.ps1

Write-Host ""
Write-Host "Génération du rapport en cours..." -ForegroundColor Yellow
Write-Host ""

# Lancer le script avec sortie non-bufferisée
python -u .\lance_un_rapport.py

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Rapport généré avec succès !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Le fichier HTML a été créé dans le dossier reports/" -ForegroundColor White
Write-Host "Ouvrez-le dans votre navigateur pour voir le rapport." -ForegroundColor White
Write-Host ""

Read-Host "Appuyez sur Entrée pour fermer"
