# 🚀 Automatisation GitHub Actions - Guide Complet

## ✅ Fichiers créés avec succès !

Les fichiers suivants ont été créés :
- ✅ `requirements.txt` - Dépendances Python
- ✅ `.github/workflows/daily-report.yml` - Workflow GitHub Actions
- ✅ `GITHUB_ACTIONS_SETUP.md` - Ce fichier d'instructions

---

## 📋 ÉTAPES À SUIVRE (dans l'ordre)

### **Étape 1 : Pousser les fichiers sur GitHub**

Ouvrez **PowerShell** dans ce dossier et exécutez :

```powershell
# Ajouter les fichiers
git add .github/
git add requirements.txt
git add GITHUB_ACTIONS_SETUP.md

# Vérifier ce qui va être commité
git status

# Commiter
git commit -m "Add GitHub Actions automation"

# Pousser sur GitHub
git push
```

**OU** utilisez **GitHub Desktop** :
1. Ouvrez GitHub Desktop
2. Sélectionnez les fichiers : `.github/`, `requirements.txt`, `GITHUB_ACTIONS_SETUP.md`
3. Écrivez le message : "Add GitHub Actions automation"
4. Cliquez sur "Commit to main"
5. Cliquez sur "Push origin"

---

### **Étape 2 : Configurer les secrets sur GitHub**

1. **Allez sur GitHub.com** et ouvrez votre dépôt

2. **Cliquez sur** : `Settings` (en haut à droite)

3. **Dans le menu de gauche** : `Secrets and variables` → `Actions`

4. **Cliquez sur** : `New repository secret`

5. **Ajoutez ces 6 secrets** (un par un) :

#### Secret 1 : SPIDER_VISION_API_BASE
- **Name** : `SPIDER_VISION_API_BASE`
- **Secret** : `https://food-api-spider-vision.data-solutions.com`
- Cliquez sur `Add secret`

#### Secret 2 : SPIDER_VISION_EMAIL
- **Name** : `SPIDER_VISION_EMAIL`
- **Secret** : Votre email SpiderVision (depuis votre fichier `.env`)
- Cliquez sur `Add secret`

#### Secret 3 : SPIDER_VISION_PASSWORD
- **Name** : `SPIDER_VISION_PASSWORD`
- **Secret** : Votre mot de passe SpiderVision (depuis votre fichier `.env`)
- Cliquez sur `Add secret`

#### Secret 4 : SPIDER_VISION_JWT_TOKEN (optionnel)
- **Name** : `SPIDER_VISION_JWT_TOKEN`
- **Secret** : Votre token JWT (depuis votre fichier `.env`)
- Cliquez sur `Add secret`
- ⚠️ **Note** : Si vous avez un token JWT, vous n'avez pas besoin de EMAIL et PASSWORD

#### Secret 5 : SPIDER_VISION_LOGIN_ENDPOINT
- **Name** : `SPIDER_VISION_LOGIN_ENDPOINT`
- **Secret** : `/admin-user/sign-in`
- Cliquez sur `Add secret`

#### Secret 6 : SPIDER_VISION_OVERVIEW_ENDPOINT
- **Name** : `SPIDER_VISION_OVERVIEW_ENDPOINT`
- **Secret** : `/store-history/overview`
- Cliquez sur `Add secret`

---

### **Étape 3 : Tester le workflow immédiatement**

1. **Sur GitHub**, cliquez sur l'onglet **`Actions`** (en haut)

2. **Dans la liste de gauche**, cliquez sur **`📊 Daily SpiderVision Report`**

3. **Cliquez sur le bouton** `Run workflow` (à droite)

4. **Sélectionnez** `Branch: main`

5. **Cliquez sur** le bouton vert `Run workflow`

6. **Attendez quelques secondes**, puis **rafraîchissez la page**

7. **Vous verrez** un workflow en cours d'exécution (icône jaune 🟡)

8. **Cliquez dessus** pour voir les logs en temps réel

9. **Une fois terminé** (icône verte ✅), cliquez sur **`Artifacts`** en bas pour télécharger le rapport

---

### **Étape 4 : Vérifier que tout fonctionne**

#### ✅ Le workflow a réussi si :
- Icône verte ✅ à côté du workflow
- Vous pouvez télécharger l'artifact `spidervision-report-X`
- Le fichier HTML est présent dans l'artifact

#### ❌ Le workflow a échoué si :
- Icône rouge ❌ à côté du workflow
- Consultez les logs pour voir l'erreur
- Vérifiez que tous les secrets sont bien configurés

---

## 🎉 C'est terminé !

### **Résultat :**

Votre rapport sera maintenant généré **automatiquement tous les jours à 09:30** (heure de Paris) avec :

- ✅ **Exécution cloud** (même si votre PC est éteint)
- ✅ **Logs détaillés** dans l'onglet Actions
- ✅ **Rapports téléchargeables** (conservés 30 jours)
- ✅ **Exécution manuelle** possible à tout moment
- ✅ **Notifications par email** en cas d'échec (configurable)

---

## 📊 Accéder aux rapports

### **Rapports quotidiens :**
1. Allez sur GitHub → Actions
2. Cliquez sur le workflow du jour
3. Téléchargez l'artifact en bas de page
4. Décompressez le ZIP
5. Ouvrez le fichier HTML dans votre navigateur

### **Historique :**
Tous les rapports des 30 derniers jours sont disponibles dans l'onglet Actions.

---

## 🔧 Dépannage

### **Le workflow ne démarre pas :**
- Vérifiez que vous avez bien poussé les fichiers sur GitHub
- Vérifiez que le fichier `.github/workflows/daily-report.yml` existe sur GitHub

### **Le workflow échoue avec "Authentication failed" :**
- Vérifiez que les secrets sont bien configurés
- Vérifiez que l'email et le mot de passe sont corrects
- Ou vérifiez que le JWT_TOKEN est valide

### **Le workflow échoue avec "Module not found" :**
- Vérifiez que `requirements.txt` contient toutes les dépendances
- Le workflow devrait installer automatiquement les dépendances

---

## 📧 Support

Si vous rencontrez des problèmes, consultez les logs du workflow sur GitHub Actions.

**Bon automatisation ! 🚀**
