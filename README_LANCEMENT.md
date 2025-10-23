# 🚀 SpiderVision Report - Lancement et Automatisation

## 📁 Fichiers de lancement créés :

### **Option 1 - Fichier BAT Automatisé (NOUVEAU)**
```
lancer_rapport.bat
```
**Double-clic** sur ce fichier pour :
- Activer automatiquement l'environnement Python
- Générer le rapport avec les données live
- Créer des logs détaillés dans le dossier `logs/`
- Fonctionne en mode automatique (sans pause)

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
2. **Exécution** de `generate_new_report.py`
3. **Génération** du rapport HTML dans `reports/`
4. **Création de logs** dans `logs/rapport_YYYYMMDD_HHMMSS.log`
5. **Gestion des erreurs** automatique

## 📊 Résultat attendu :

Un fichier HTML sera créé dans `reports/` avec le nom :
```
last_day_history_live_report_YYYYMMDD_HHMMSS.html
```

Un fichier log sera créé dans `logs/` avec le nom :
```
rapport_YYYYMMDD_HHMMSS.log
```

## ⚡ Utilisation Manuelle :

**Simple double-clic** sur `lancer_rapport.bat` et c'est tout !

Le rapport contiendra :
- ✅ 36 retailers avec données live
- ✅ Jauges de progression visuelles
- ✅ Statut global (pire entre Progress/Success)
- ✅ Filtrage interactif
- ✅ Design moderne et responsive

## 🤖 Automatisation Quotidienne :

### **Configuration du Planificateur de Tâches Windows**

1. **Ouvrir le Planificateur** :
   - Appuyez sur `Windows + R`
   - Tapez : `taskschd.msc`
   - Appuyez sur Entrée

2. **Créer une tâche** :
   - Cliquez sur "Créer une tâche..." (à droite)
   - **Nom** : `Rapport SpiderVision Quotidien`
   - ✅ Cochez : "Exécuter avec les autorisations maximales"

3. **Configurer le déclencheur** :
   - Onglet "Déclencheurs" → "Nouveau..."
   - **Quotidienne** à l'heure souhaitée (ex: 09:30)
   - ✅ Cochez : "Activé"

4. **Configurer l'action** :
   - Onglet "Actions" → "Nouveau..."
   - **Programme** : `C:\Users\cmass\Desktop\Projet dealer report\lancer_rapport.bat`
   - **Commencer dans** : `C:\Users\cmass\Desktop\Projet dealer report`

5. **Paramètres** :
   - Onglet "Conditions" : Décochez "Uniquement si relié au secteur"
   - Onglet "Paramètres" : Cochez "Autoriser l'exécution à la demande"

6. **Tester** :
   - Clic droit sur la tâche → "Exécuter"
   - Vérifiez le fichier log dans `logs/`

## 📝 Consulter les Logs :

Les logs sont créés automatiquement dans le dossier `logs/` :
```
logs/
  rapport_20251021_093000.log
  rapport_20251022_093000.log
  ...
```

Chaque log contient :
- Date et heure d'exécution
- Étapes d'activation de l'environnement
- Sortie complète de la génération du rapport
- Statut de succès ou d'erreur
- Code d'erreur si échec

## 🔧 En cas de problème :

Si le script ne fonctionne pas :
1. Vérifier que `.venv` existe
2. Consulter le dernier fichier log dans `logs/`
3. Vérifier que le token est configuré dans `.env`
4. Relancer `setup_env.bat` si nécessaire

## 🎉 Résultat de l'automatisation :

Une fois configuré, le rapport sera généré automatiquement tous les jours avec :
- ✅ Génération silencieuse (pas de fenêtre)
- ✅ Logs détaillés pour le suivi
- ✅ Gestion automatique des erreurs
- ✅ Historique complet des exécutions
