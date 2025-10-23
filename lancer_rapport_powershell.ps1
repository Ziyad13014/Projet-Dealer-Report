# Git Push GitHub Actions - PowerShell
# Script pour pousser les fichiers d'automatisation sur GitHub

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "   GIT COMMIT ET PUSH" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Changer vers le répertoire du script
Set-Location $PSScriptRoot

Write-Host "Ajout des fichiers..." -ForegroundColor Yellow
git add .github/ requirements.txt GITHUB_ACTIONS_SETUP.md

Write-Host ""
Write-Host "Commit..." -ForegroundColor Yellow
git commit -m "Add GitHub Actions automation"

Write-Host ""
Write-Host "Push vers GitHub..." -ForegroundColor Yellow
git push

Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "TERMINE !" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Les fichiers ont ete pousses sur GitHub." -ForegroundColor White
Write-Host ""
Write-Host "Prochaines etapes:" -ForegroundColor Yellow
Write-Host "1. Allez sur GitHub - Settings - Secrets" -ForegroundColor White
Write-Host "2. Ajoutez les secrets (voir GITHUB_ACTIONS_SETUP.md)" -ForegroundColor White
Write-Host "3. Testez le workflow dans Actions" -ForegroundColor White
Write-Host ""

Read-Host "Appuyez sur Entree pour fermer"
