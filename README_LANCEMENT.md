# 🚀 SpiderVision Report - Lancement en 1 clic

## 📁 Fichiers de lancement créés :

### **Option 1 - Fichier BAT (recommandé)**
```
lancer_rapport.bat
```
**Double-clic** sur ce fichier pour :
- Activer automatiquement l'environnement Python
- Générer le rapport avec les données live
- Afficher le résultat dans une fenêtre colorée

### **Option 2 - Script PowerShell**
```
lancer_rapport_powershell.ps1
```
**Clic-droit → "Exécuter avec PowerShell"** pour :
- Interface PowerShell avec couleurs
- Même fonctionnalités que le BAT
- Plus d'informations de debug

### **Option 3 - Script Python (alias)**
```
python lance_un_rapport.py
```
- Appelle le générateur de rapport (generate_new_report.py)
- Produit un fichier HTML dans le dossier reports/

## 🎯 Ce que font ces scripts :

1. **Activation automatique** de l'environnement `.venv`
2. **Exécution** de `generate_last_day_report.py`
3. **Génération** du rapport HTML dans `reports/`
4. **Affichage** du statut de réussite
5. **Pause** pour voir les résultats

## 📊 Résultat attendu :

Un fichier HTML sera créé dans `reports/` avec le nom :
```
last_day_history_live_report_YYYYMMDD_HHMMSS.html
```

## ⚡ Utilisation :

**Simple double-clic** sur `lancer_rapport.bat` et c'est tout !

Le rapport contiendra :
- ✅ 36 retailers avec données live
- ✅ Jauges de progression visuelles
- ✅ Statut global (pire entre Progress/Success)
- ✅ Filtrage interactif
- ✅ Design moderne et responsive

## 🔧 En cas de problème :

Si le script ne fonctionne pas :
1. Vérifier que `.venv` existe
2. Relancer `setup_env.bat` d'abord
3. Utiliser le rapport démo : `demo_rapport_jauges_20250916_100956.html`
