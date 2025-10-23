# 📚 Documentation Complète - Projet SpiderVision Dealer Report

## 📋 Table des matières

1. [Vue d'ensemble](#vue-densemble)
2. [Architecture du projet](#architecture-du-projet)
3. [Fichiers principaux](#fichiers-principaux)
4. [Dossiers et leur contenu](#dossiers-et-leur-contenu)
5. [Flux de fonctionnement](#flux-de-fonctionnement)
6. [Configuration](#configuration)
7. [Utilisation](#utilisation)
8. [Maintenance](#maintenance)

---

## 🎯 Vue d'ensemble

### **Objectif du projet**
Système automatisé de génération de rapports quotidiens pour le suivi des dealers SpiderVision. Le système récupère les données depuis l'API SpiderVision, génère un rapport HTML interactif et maintient un historique des rapports.

### **Technologies utilisées**
- **Python 3.12+** - Langage principal
- **Requests** - Appels API
- **Python-dotenv** - Gestion des variables d'environnement
- **GitHub Actions** - Automatisation quotidienne
- **HTML/CSS/JavaScript** - Interface du rapport

---

## 🏗️ Architecture du projet

```
Projet-Dealer-Report/
├── 📁 .github/workflows/          # Automatisation GitHub Actions
│   └── daily-report.yml           # Workflow de génération quotidienne
│
├── 📁 src/                        # Code source principal
│   ├── generate_new_report.py     # Script principal de génération
│   ├── update_index_link.py       # Mise à jour de index.html
│   └── cli/                       # Modules CLI
│       ├── services/              # Services (auth, data, export)
│       └── repository/            # Accès aux données
│
├── 📁 scripts/                    # Scripts utilitaires
│   ├── lancer_rapport.bat         # Script Windows tout-en-un
│   ├── generer_nouveau_token.py   # Génération token JWT
│   ├── decode_jwt.py              # Décodage token JWT
│   └── setup_env.bat              # Configuration environnement
│
├── 📁 reports/                    # Rapports générés
│   ├── last_day_history_live_report_*.html  # Rapports horodatés
│   ├── last_day_history_live_report.html    # Lien permanent
│   └── spider_vision_overview_current.csv   # Données brutes
│
├── 📁 docs/                       # Documentation
│   ├── DOCUMENTATION_COMPLETE.md  # Ce fichier
│   ├── GITHUB_ACTIONS_SETUP.md    # Configuration GitHub Actions
│   └── README.md                  # Index de la documentation
│
├── 📁 logs/                       # Logs d'exécution
│   └── rapport_*.log              # Logs horodatés
│
├── 📁 archive/                    # Fichiers archivés
│   └── old_scripts/               # Anciens scripts
│
├── 📄 .env                        # Variables d'environnement (ignoré par git)
├── 📄 .gitignore                  # Fichiers ignorés par git
├── 📄 requirements.txt            # Dépendances Python
├── 📄 index.html                  # Page d'accueil
├── 📄 README.md                   # Documentation principale
└── 📄 REORGANISATION.md           # Historique de réorganisation
```

---

## 📄 Fichiers principaux

### **1. Fichiers à la racine**

#### **`.env`** 🔐
**Rôle** : Contient les variables d'environnement sensibles (credentials, tokens)

**Contenu** :
```bash
SPIDER_VISION_API_BASE=https://food-api-spider-vision.data-solutions.com
SPIDER_VISION_EMAIL=crawl@wiser.com
SPIDER_VISION_PASSWORD=cra@01012024?
SPIDER_VISION_JWT_TOKEN=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
SPIDER_VISION_LOGIN_ENDPOINT=/admin-user/sign-in
SPIDER_VISION_OVERVIEW_ENDPOINT=/store-history/overview
```

**Important** :
- ⚠️ **Jamais commité sur Git** (dans `.gitignore`)
- 🔄 Le token JWT est mis à jour automatiquement par `generer_nouveau_token.py`
- 🔑 Les credentials sont utilisés pour générer un nouveau token

---

#### **`.gitignore`** 🚫
**Rôle** : Définit les fichiers à ignorer par Git

**Contenu important** :
```bash
.env              # Variables d'environnement
.env.*            # Toutes les variantes de .env
__pycache__/      # Cache Python
.venv/            # Environnement virtuel
logs/             # Logs d'exécution
*.pyc             # Fichiers compilés Python
```

**Pourquoi** : Évite de commiter des données sensibles ou temporaires

---

#### **`requirements.txt`** 📦
**Rôle** : Liste toutes les dépendances Python du projet

**Contenu** :
```
click
python-dotenv
dependency-injector
PyMySQL
requests
```

**Utilisation** :
```bash
pip install -r requirements.txt
```

---

#### **`index.html`** 🏠
**Rôle** : Page d'accueil du projet, point d'entrée pour accéder aux rapports

**Fonctionnalités** :
- 🔗 Lien vers le dernier rapport généré
- 📂 Lien vers le dossier des rapports
- 🎨 Design moderne et responsive
- 🔄 Mis à jour automatiquement par `update_index_link.py`

**Mise à jour automatique** :
Le lien vers le dernier rapport est mis à jour à chaque génération :
```html
<a href="reports/last_day_history_live_report_20251023_152338.html">
    📈 Voir le Dernier Rapport
</a>
```

---

#### **`README.md`** 📖
**Rôle** : Documentation principale du projet

**Contenu** :
- 🚀 Guide de démarrage rapide
- 📋 Instructions d'utilisation
- 🏗️ Structure du projet
- 🔧 Configuration requise
- 📊 Exemples d'utilisation

---

#### **`REORGANISATION.md`** 📝
**Rôle** : Historique de la réorganisation du projet

**Contenu** :
- 📅 Date de réorganisation
- 📁 Fichiers déplacés/archivés
- ✅ Améliorations apportées
- 🔄 Changements de structure

---

### **2. Dossier `.github/workflows/`**

#### **`daily-report.yml`** ⚙️
**Rôle** : Workflow GitHub Actions pour la génération automatique quotidienne

**Déclenchement** :
- ⏰ **Automatique** : Tous les jours à 09:30 (heure de Paris)
- 🖱️ **Manuel** : Via l'interface GitHub Actions

**Étapes du workflow** :
1. **Checkout code** : Récupère le code du repository
2. **Setup Python** : Installe Python 3.12
3. **Install dependencies** : Installe les packages Python
4. **Generate new JWT token** : Génère un token frais
5. **Generate report** : Génère le rapport HTML
6. **Upload artifacts** : Sauvegarde les rapports générés
7. **Create summary** : Crée un résumé dans GitHub

**Variables d'environnement requises** :
```yaml
SPIDER_VISION_API_BASE
SPIDER_VISION_EMAIL
SPIDER_VISION_PASSWORD
SPIDER_VISION_LOGIN_ENDPOINT
SPIDER_VISION_OVERVIEW_ENDPOINT
```

**Note** : `SPIDER_VISION_JWT_TOKEN` n'est plus nécessaire car le token est généré automatiquement

---

### **3. Dossier `src/`**

#### **`src/generate_new_report.py`** 🎯
**Rôle** : Script principal qui génère le rapport HTML

**Fonctionnalités** :
1. **Authentification API** : Se connecte à l'API SpiderVision
2. **Récupération données** : Récupère les données des 36 dealers
3. **Génération HTML** : Crée un rapport HTML interactif
4. **Sauvegarde CSV** : Exporte les données en CSV
5. **Nettoyage** : Supprime les rapports anciens (garde les 10 derniers)
6. **Mise à jour index** : Met à jour `index.html` avec le nouveau lien

**Flux d'exécution** :
```python
1. Charger les variables d'environnement (.env)
2. Authentifier avec l'API (via token JWT ou email/password)
3. Récupérer les données des dealers
4. Générer le fichier HTML avec les données
5. Sauvegarder le CSV
6. Nettoyer les anciens rapports
7. Mettre à jour index.html
```

**Fonctions principales** :
- `get_live_data_from_api()` : Récupère les données depuis l'API
- `generate_new_report()` : Fonction principale
- `get_logo_base64()` : Convertit le logo en base64

**Gestion des erreurs** :
- Si l'API échoue, tente de lire le CSV local en fallback
- Affiche des messages d'erreur clairs avec emojis

---

#### **`src/update_index_link.py`** 🔗
**Rôle** : Met à jour le lien dans `index.html` vers le dernier rapport

**Fonctionnement** :
1. Trouve le dernier rapport dans `reports/`
2. Lit `index.html`
3. Remplace l'ancien lien par le nouveau
4. Met à jour le fichier permanent `last_day_history_live_report.html`

**Fonction principale** :
```python
def auto_update_index():
    # Trouve le dernier rapport
    latest_report = find_latest_report()
    
    # Met à jour index.html
    update_index_html(latest_report)
    
    # Met à jour le lien permanent
    update_permanent_link(latest_report)
```

---

#### **`src/cli/services/auth.py`** 🔐
**Rôle** : Gère l'authentification avec l'API SpiderVision

**Classe principale** : `SpiderVisionAuth`

**Méthodes** :
- `__init__()` : Initialise avec les credentials du `.env`
- `login(email, password)` : Se connecte et récupère un token JWT
- `get_token()` : Retourne le token actuel
- `is_authenticated()` : Vérifie si authentifié
- `logout()` : Déconnexion

**Fonctionnement** :
```python
# Si un token JWT existe dans .env, l'utiliser
if self._token:
    return self._token

# Sinon, se connecter avec email/password
response = requests.post(login_url, json={
    "email": email,
    "password": password
})

# Extraire le token de la réponse
token = response.json()["token"]
return token
```

---

#### **`src/cli/services/data.py`** 📊
**Rôle** : Gère la récupération des données depuis l'API

**Classe principale** : `SpiderVisionDataService`

**Méthodes** :
- `get_overview(token)` : Récupère les données overview des dealers
- `parse_response(data)` : Parse la réponse JSON de l'API

**Utilisation** :
```python
data_service = SpiderVisionDataService()
overview_data = data_service.get_overview(token)
```

---

#### **`src/cli/repository/WebDataRepository.py`** 🗄️
**Rôle** : Repository pour l'accès aux données web

**Fonctionnalités** :
- Abstraction de l'accès aux données
- Gestion du cache
- Transformation des données

---

### **4. Dossier `scripts/`**

#### **`scripts/lancer_rapport.bat`** 🚀
**Rôle** : Script Windows tout-en-un pour générer un rapport

**Fonctionnalités** :
1. Active l'environnement virtuel Python
2. Génère un nouveau token JWT
3. Génère le rapport HTML
4. Enregistre les logs dans `logs/`

**Utilisation** :
```bash
scripts\lancer_rapport.bat
```

**Avantages** :
- ✅ Une seule commande pour tout
- ✅ Logs automatiques
- ✅ Gestion d'erreurs
- ✅ Token toujours frais

**Contenu** :
```batch
@echo off
cd /d "%~dp0\.."

# Active l'environnement virtuel
call .venv\Scripts\activate.bat

# Génère un nouveau token
python scripts\generer_nouveau_token.py

# Génère le rapport
python src\generate_new_report.py

# Désactive l'environnement
call .venv\Scripts\deactivate.bat
```

---

#### **`scripts/generer_nouveau_token.py`** 🔑
**Rôle** : Génère un nouveau token JWT et met à jour le `.env`

**Fonctionnalités** :
1. Se connecte à l'API avec email/password
2. Récupère un nouveau token JWT
3. Met à jour automatiquement le fichier `.env`
4. Affiche le token (partiellement masqué)

**Fonctions principales** :
- `generate_new_jwt_token()` : Génère le token
- `update_env_token(token)` : Met à jour le `.env`

**Utilisation** :
```bash
python scripts\generer_nouveau_token.py
```

**Sortie** :
```
🔑 Génération d'un nouveau token JWT...
📧 Email utilisé: cra***@wiser.com
🔐 Password: ************* (13 caractères)
✅ Authentification réussie !
🔄 Mise à jour automatique du fichier .env...
✅ Fichier .env mis à jour avec succès !
```

**Sécurité** :
- Le token complet n'est affiché que partiellement
- Le password est masqué
- Le `.env` est protégé par `.gitignore`

---

#### **`scripts/decode_jwt.py`** 🔍
**Rôle** : Utilitaire pour décoder et analyser un token JWT

**Fonctionnalités** :
- Décode le header et payload du token
- Affiche les informations utilisateur
- Vérifie la date d'expiration
- Affiche les rôles et permissions

**Utilisation** :
```bash
python scripts\decode_jwt.py
```

**Sortie** :
```
🔍 ANALYSE DU TOKEN JWT
📋 HEADER: {"alg": "HS256", "typ": "JWT"}
📦 PAYLOAD: {"sub": 203, "roles": ["adminUser"], ...}
👤 User ID: 203
🔑 Rôles: ['adminUser']
📅 Créé le: 2025-10-23 14:40:00
⏰ Expire le: 2025-10-23 16:40:00
   ✅ Token valide encore 1:59:35
```

**Utilité** :
- Vérifier si un token est expiré
- Voir les informations contenues dans le token
- Debug des problèmes d'authentification

---

#### **`scripts/setup_env.bat`** ⚙️
**Rôle** : Script de configuration initiale de l'environnement

**Fonctionnalités** :
- Crée l'environnement virtuel Python
- Installe les dépendances
- Configure les variables d'environnement

**Utilisation** :
```bash
scripts\setup_env.bat
```

---

### **5. Dossier `reports/`**

#### **`reports/last_day_history_live_report_YYYYMMDD_HHMMSS.html`** 📊
**Rôle** : Rapports HTML horodatés

**Nom** : Format `last_day_history_live_report_20251023_152338.html`
- `20251023` : Date (23 octobre 2025)
- `152338` : Heure (15:23:38)

**Contenu** :
- Tableau interactif des 36 dealers
- Filtres par statut (Tous, Succès, Avertissement, Erreur)
- Barres de progression colorées
- Historique sur 6 jours
- Détails expandables pour chaque dealer

**Design** :
- 🌙 Thème sombre moderne
- 📱 Responsive (mobile-friendly)
- 🎨 Animations et transitions
- 🔍 Recherche et filtres

---

#### **`reports/last_day_history_live_report.html`** 🔗
**Rôle** : Lien permanent vers le dernier rapport

**Fonctionnement** :
- Copie du dernier rapport généré
- Toujours à jour
- URL stable pour les bookmarks

**Utilité** :
- Avoir une URL fixe qui pointe toujours vers le dernier rapport
- Facilite le partage et les bookmarks

---

#### **`reports/spider_vision_overview_current.csv`** 📄
**Rôle** : Données brutes au format CSV

**Contenu** :
- Toutes les données des 36 dealers
- Format CSV pour analyse dans Excel/Python
- Mis à jour à chaque génération

**Colonnes** :
```
crawlProgress, crawlProgressWithSpread, crawlSuccessProgress,
day0, day1, day2, day3, day4, day5,
domainDealerId, domainDealerLogo, domainDealerName,
storeCount, storeCountWithSpread, storeFailedCount,
storeInDeltaCount, storeToCrawl, successCount
```

---

### **6. Dossier `logs/`**

#### **`logs/rapport_YYYYMMDD_HHMMSS.log`** 📝
**Rôle** : Logs d'exécution horodatés

**Contenu** :
- Toutes les étapes d'exécution
- Messages de succès/erreur
- Timestamps précis
- Informations de debug

**Exemple** :
```
=========================================
Generation rapport quotidien SpiderVision
Date: 23/10/2025 16:22:08
=========================================

[INFO] Activation environnement virtuel...
[INFO] Environnement active avec succes
[INFO] Generation d'un nouveau token JWT...
✅ Authentification réussie !
[INFO] Generation du rapport en cours...
✅ 36 récupérées depuis l'API
✅ Nouveau rapport généré
[SUCCES] Rapport genere avec succes !
```

**Utilité** :
- Debug des problèmes
- Audit des exécutions
- Historique des générations

---

### **7. Dossier `docs/`**

#### **`docs/DOCUMENTATION_COMPLETE.md`** 📚
**Rôle** : Ce fichier - Documentation exhaustive du projet

---

#### **`docs/GITHUB_ACTIONS_SETUP.md`** ⚙️
**Rôle** : Guide de configuration de GitHub Actions

**Contenu** :
- Configuration des secrets
- Explication du workflow
- Troubleshooting
- Bonnes pratiques

---

#### **`docs/README.md`** 📖
**Rôle** : Index de la documentation

**Contenu** :
- Liste de tous les documents
- Liens vers chaque guide
- Organisation de la documentation

---

### **8. Dossier `archive/`**

#### **`archive/old_scripts/`** 📦
**Rôle** : Anciens scripts archivés lors de la réorganisation

**Contenu** :
- 40+ fichiers de test obsolètes
- Anciens scripts de debug
- Fichiers dupliqués
- Code expérimental

**Pourquoi archivé** :
- Nettoyer le projet
- Garder l'historique
- Référence future si besoin

---

## 🔄 Flux de fonctionnement

### **Génération locale d'un rapport**

```
1. Utilisateur lance : scripts\lancer_rapport.bat
   ↓
2. Script active l'environnement virtuel Python
   ↓
3. Script appelle : python scripts\generer_nouveau_token.py
   ↓
4. generer_nouveau_token.py :
   - Se connecte à l'API avec email/password
   - Récupère un nouveau token JWT
   - Met à jour le fichier .env
   ↓
5. Script appelle : python src\generate_new_report.py
   ↓
6. generate_new_report.py :
   - Lit le token depuis .env
   - Se connecte à l'API SpiderVision
   - Récupère les données des 36 dealers
   - Génère le fichier HTML
   - Sauvegarde le CSV
   - Nettoie les anciens rapports (garde 10)
   - Met à jour index.html
   ↓
7. Logs enregistrés dans logs/rapport_*.log
   ↓
8. ✅ Rapport disponible dans reports/
```

---

### **Génération automatique via GitHub Actions**

```
1. Déclenchement : Tous les jours à 09:30 (ou manuel)
   ↓
2. GitHub Actions checkout le code
   ↓
3. Installation de Python 3.12 et dépendances
   ↓
4. Exécution : python scripts/generer_nouveau_token.py
   - Génère un nouveau token JWT
   - Met à jour .env (dans l'environnement GitHub)
   ↓
5. Exécution : python src/generate_new_report.py
   - Génère le rapport avec le token frais
   ↓
6. Upload des artifacts :
   - Rapport HTML
   - CSV des données
   - index.html
   ↓
7. Création d'un résumé dans GitHub
   ↓
8. ✅ Rapport disponible dans les artifacts GitHub
```

---

## ⚙️ Configuration

### **Variables d'environnement (`.env`)**

| Variable | Description | Exemple |
|----------|-------------|---------|
| `SPIDER_VISION_API_BASE` | URL de base de l'API | `https://food-api-spider-vision.data-solutions.com` |
| `SPIDER_VISION_EMAIL` | Email de connexion | `crawl@wiser.com` |
| `SPIDER_VISION_PASSWORD` | Mot de passe | `cra@01012024?` |
| `SPIDER_VISION_JWT_TOKEN` | Token JWT (mis à jour auto) | `eyJhbGciOiJIUzI1NiIs...` |
| `SPIDER_VISION_LOGIN_ENDPOINT` | Endpoint de login | `/admin-user/sign-in` |
| `SPIDER_VISION_OVERVIEW_ENDPOINT` | Endpoint des données | `/store-history/overview` |

---

### **Secrets GitHub Actions**

Pour configurer les secrets sur GitHub :

1. Allez sur : `https://github.com/Ziyad13014/Projet-Dealer-Report/settings/secrets/actions`
2. Cliquez sur : `New repository secret`
3. Ajoutez chaque secret :

| Secret | Valeur |
|--------|--------|
| `SPIDER_VISION_API_BASE` | `https://food-api-spider-vision.data-solutions.com` |
| `SPIDER_VISION_EMAIL` | `crawl@wiser.com` |
| `SPIDER_VISION_PASSWORD` | `cra@01012024?` |
| `SPIDER_VISION_LOGIN_ENDPOINT` | `/admin-user/sign-in` |
| `SPIDER_VISION_OVERVIEW_ENDPOINT` | `/store-history/overview` |

**Note** : `SPIDER_VISION_JWT_TOKEN` n'est plus nécessaire !

---

## 🚀 Utilisation

### **Génération locale**

#### **Option 1 : Script tout-en-un (recommandé)**
```bash
scripts\lancer_rapport.bat
```

#### **Option 2 : Étapes manuelles**
```bash
# Étape 1 : Générer un nouveau token
python scripts\generer_nouveau_token.py

# Étape 2 : Générer le rapport
python src\generate_new_report.py
```

---

### **Génération via GitHub Actions**

#### **Déclenchement manuel**
1. Allez sur : `https://github.com/Ziyad13014/Projet-Dealer-Report/actions`
2. Cliquez sur : `📊 Daily SpiderVision Report`
3. Cliquez sur : `Run workflow`
4. Cliquez sur : `Run workflow` (bouton vert)

#### **Déclenchement automatique**
- Tous les jours à 09:30 (heure de Paris)
- Configuré dans `.github/workflows/daily-report.yml`

---

### **Consulter un rapport**

#### **Option 1 : Via index.html**
1. Ouvrez `index.html` dans votre navigateur
2. Cliquez sur "📈 Voir le Dernier Rapport"

#### **Option 2 : Directement**
1. Allez dans le dossier `reports/`
2. Ouvrez le fichier le plus récent

#### **Option 3 : Lien permanent**
1. Ouvrez `reports/last_day_history_live_report.html`
2. Toujours à jour avec le dernier rapport

---

## 🔧 Maintenance

### **Nettoyage automatique**

Le système garde automatiquement les **10 rapports les plus récents** et supprime les anciens.

Pour changer ce nombre, modifiez dans `src/generate_new_report.py` :
```python
max_reports = 10  # Changez ce nombre
```

---

### **Renouvellement du token**

Le token JWT expire après **2 heures**. Le système le renouvelle automatiquement :

- **Local** : À chaque exécution de `lancer_rapport.bat`
- **GitHub Actions** : À chaque exécution du workflow

Pour renouveler manuellement :
```bash
python scripts\generer_nouveau_token.py
```

---

### **Vérifier un token**

Pour vérifier si un token est valide :
```bash
python scripts\decode_jwt.py
```

---

### **Logs**

Les logs sont dans `logs/rapport_*.log`

Pour voir le dernier log :
```bash
# Windows
type logs\rapport_*.log | findstr /C:"[SUCCES]" /C:"[ERREUR]"
```

---

## 🐛 Troubleshooting

### **Problème : Token expiré**

**Symptôme** :
```
❌ Erreur 401 - Unauthorized
```

**Solution** :
```bash
python scripts\generer_nouveau_token.py
```

---

### **Problème : API inaccessible**

**Symptôme** :
```
❌ Impossible de générer le rapport : l'API SpiderVision n'est pas disponible
```

**Solutions** :
1. Vérifiez votre connexion internet
2. Vérifiez que l'API est en ligne
3. Le script utilisera le CSV local en fallback

---

### **Problème : Erreur d'encodage (emojis)**

**Symptôme** :
```
UnicodeEncodeError: 'charmap' codec can't encode character
```

**Solution** :
Déjà corrigé dans les scripts avec :
```python
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
```

---

## 📊 Statistiques du projet

- **Fichiers Python** : 15+
- **Scripts utilitaires** : 4
- **Lignes de code** : ~3000
- **Dealers suivis** : 36
- **Rapports conservés** : 10 derniers
- **Fréquence** : Quotidienne (09:30)
- **Durée d'exécution** : ~2-3 secondes

---

## 🎯 Améliorations futures possibles

1. **Notifications** : Envoyer un email/Teams quand un dealer est en erreur
2. **Dashboard** : Interface web pour visualiser l'historique
3. **Alertes** : Système d'alertes pour les erreurs critiques
4. **Export** : Export en PDF ou Excel
5. **API** : API REST pour accéder aux données
6. **Base de données** : Stocker l'historique dans une DB

---

## 📞 Support

Pour toute question ou problème :
1. Consultez cette documentation
2. Vérifiez les logs dans `logs/`
3. Testez avec `decode_jwt.py` pour vérifier le token
4. Consultez les issues GitHub

---

**Documentation mise à jour le : 23 octobre 2025**
**Version du projet : 2.0**
**Auteur : Ziyad13014**
