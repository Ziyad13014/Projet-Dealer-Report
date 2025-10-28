# 📊 SpiderVision Dealer Report

Système automatisé de génération de rapports quotidiens pour le suivi des dealers SpiderVision.

## 🚀 Démarrage rapide

### **Génération manuelle d'un rapport**

#### **Option 1 : Script automatique complet (recommandé)**
```bash
# Windows - Génère un nouveau token ET le rapport automatiquement
scripts\lancer_rapport.bat
```

Ce script fait automatiquement :
1. ✅ Génère un nouveau token JWT
2. ✅ Met à jour le fichier `.env`
3. ✅ Génère le rapport HTML
4. ✅ Enregistre les logs dans `logs/`

#### **Option 2 : Génération manuelle en 2 étapes**
```bash
# Étape 1 : Générer un nouveau token (met à jour .env automatiquement)
python scripts\generer_nouveau_token.py

# Étape 2 : Générer le rapport
python src\generate_new_report.py
```

**Note** : Le système conserve automatiquement les **10 rapports les plus récents** et supprime les plus anciens.

### **Automatisation quotidienne**
Le rapport est généré automatiquement tous les jours à 09:30 via GitHub Actions.
Consultez `docs/GITHUB_ACTIONS_SETUP.md` pour la configuration.

## 📁 Structure du projet

```
Projet-Dealer-Report/
├── 📁 src/                          # Code source principal
│   ├── generate_new_report.py       # ✅ Script principal de génération
│   ├── update_index_link.py         # Mise à jour automatique de index.html
│   └── cli/                         # Module CLI (services, repository, etc.)
│
├── 📁 scripts/                      # Scripts d'automatisation
│   ├── lancer_rapport.bat           # Script Windows tout-en-un
│   ├── generer_nouveau_token.py     # Génération token JWT
│   └── setup_env.bat                # Configuration environnement
│
├── 📁 docs/                         # Documentation
│   ├── README_LANCEMENT.md          # Guide de lancement
│   └── GITHUB_ACTIONS_SETUP.md      # Configuration GitHub Actions
│
├── 📁 reports/                      # Rapports générés (HTML/CSV)
├── 📁 logs/                         # Logs d'exécution
├── 📁 db/                           # Schémas base de données
├── 📁 .github/workflows/            # GitHub Actions (automatisation)
│
├── .env                             # Configuration (non versionné)
├── .gitignore
├── requirements.txt                 # Dépendances Python
├── pyproject.toml                   # Configuration projet
├── index.html                       # Page d'accueil des rapports
└── README.md                        # Ce fichier
```

## Architecture

```
SpiderVision API → Report Generation → HTML/CSV → GitHub Actions
     ↓                    ↓              ↓            ↓
Authentication      Live Data      Reports      Daily Schedule
JWT Token           36 Retailers   Visual       09:30 Paris
```

## Explications rapides (FR)

- Objectif: Générer chaque jour un rapport d’anomalies des distributeurs (retailers) à partir de données MySQL, puis publier le HTML sur GCS et notifier Teams.
- Trois étapes clés: (1) Génération du rapport (CSV/HTML) via la CLI, (2) Publication sur Google Cloud Storage, (3) Notification Microsoft Teams.
- Règles métiers: Taux de crawling et de contenu minimums par retailer, avec seuil succès/avertissement/erreur; tri des anomalies en premier.
- Exécution rapide: `dealer-report generate_dealer_report` (voir --help pour options), fichiers produits dans ./reports.
- Publication: `dealer-report publish_report --path ./reports/<fichier>.html` met aussi à jour une URL « latest » fixe.
- Visualisation locale alternative: `python generate_dashboard_style_report.py` génère un dashboard HTML à partir du CSV overview courant.
- Configuration: Variables d’environnement (DB, GCP, Teams, etc.) dans .env; voir tableau plus bas.

## Features

- **Three CLI Commands**: Generate reports, publish to GCS, send Teams notifications
- **Business Rules**: Per-retailer minimum success rate and progress at 09:30 Europe/Paris
- **Multiple Formats**: CSV for data analysis, HTML for human-readable reports
- **Cloud Integration**: Google Cloud Storage with fixed "latest" URLs
- **Teams Integration**: Automated notifications via webhook
- **Scheduled Execution**: Daily CircleCI workflow at 09:30 Europe/Paris
- **Docker Support**: Containerized for consistent deployment

## Quick Start

### 1. Clone and Setup

```bash
git clone <repository-url>
cd dealer-report
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -e .
```

### 2. Configure Environment

```bash
cp .env.example .env
# Edit .env with your actual values
```

### 3. Setup Database

```bash
# Create database and tables
mysql -u root -p < db/schema.sql
mysql -u root -p < db/seed_data.sql
```

### 4. Test CLI

```bash
dealer-report --help
dealer-report generate_dealer_report --help
```

## Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DB_HOST` | MySQL host | localhost |
| `DB_PORT` | MySQL port | 3306 |
| `DB_USER` | MySQL username | app_user |
| `DB_PASSWORD` | MySQL password | secret |
| `DB_NAME` | MySQL database name | analytics |
| `GCP_PROJECT` | Google Cloud project ID | my-gcp-project |
| `GCS_BUCKET` | GCS bucket name | my-analytics-bucket |
| `TEAMS_WEBHOOK_URL` | Teams webhook URL | (required) |
| `TEAMS_DEFAULT_MESSAGE` | Default notification message | Bonjour, voici le rapport du jour. |
| `REPORTS_DIR` | Local reports directory | ./reports |
| `TZ` | Timezone for 09:30 calculation | Europe/Paris |
| `INCLUDE_SUCCESSES` | Show success items in HTML | false |
| `GCS_LATEST_HTML_PATH` | Fixed GCS path for latest report | reports/daily/dealer-report-latest.html |

## CLI Usage

### Generate Reports

```bash
# Generate today's report (both CSV and HTML)
dealer-report generate_dealer_report

# Generate for specific date range
dealer-report generate_dealer_report --date-from 2024-01-01 --date-to 2024-01-31

# Generate HTML only for specific retailer
dealer-report generate_dealer_report --dealer Carrefour --fmt html

# Generate CSV only
dealer-report generate_dealer_report --fmt csv
```

### Publish to GCS

```bash
# Upload with auto-generated path
dealer-report publish_report --path ./reports/dealer-report-20240101.html

# Upload to specific bucket and path
dealer-report publish_report --path ./report.html --bucket my-bucket --dst reports/custom/report.html
```

### Send Teams Notification

```bash
# Send with default message
dealer-report push_notification_on_teams --url "https://storage.googleapis.com/bucket/report.html"

# Send with custom message
dealer-report push_notification_on_teams --url "gs://bucket/report.html" --message "Rapport urgent disponible"

# Override webhook URL
dealer-report push_notification_on_teams --url "gs://bucket/report.html" --channel-webhook "https://..."
```

## Business Logic

### Success Rate Rule
- Calculates `success_count / total_count` for crawler runs in date range
- Compares against `retailer_rules.min_success_rate`
- Zero data (total_count = 0) is treated as an anomaly

### Progress at 09:30 Rule
- Counts runs completed by 09:30 Europe/Paris on report date
- Uses `runs_plan.expected_total` or falls back to total runs for the day
- Compares `completed_by_time / expected_total` against `retailer_rules.min_progress_0930`

### Report Output
- **Errors First**: ⚠️ Anomalies shown first, sorted alphabetically by retailer
- **Optional Successes**: ✅ Success items shown if `INCLUDE_SUCCESSES=true` or per-retailer override
- **Percentage Formatting**: At most one decimal place (95%, 95.1%)

## Docker Usage

### Build Image

```bash
docker build -t dealer-report:local -f .docker/Dockerfile .
```

### Run with Environment File

```bash
docker run --rm --env-file .env dealer-report:local --help
docker run --rm --env-file .env dealer-report:local generate_dealer_report --fmt html
```

### Run Commands

```bash
# Generate report
docker run --rm --env-file .env -v $(pwd)/reports:/app/reports dealer-report:local generate_dealer_report

# Publish report (requires GCS credentials)
docker run --rm --env-file .env -v $(pwd)/reports:/app/reports dealer-report:local publish_report --path /app/reports/dealer-report-20240101.html
```

## CircleCI Setup

### 1. Environment Variables

Set these in CircleCI project settings or context `dealer-report-prod`:

```bash
# Database
DB_HOST=your-mysql-host
DB_USER=your-mysql-user
DB_PASSWORD=your-mysql-password
DB_NAME=analytics

# GCP
GCP_PROJECT=your-gcp-project
GCS_BUCKET=your-gcs-bucket
GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json  # Optional

# Teams
TEAMS_WEBHOOK_URL=https://outlook.office.com/webhook/...

# Docker (if using custom registry)
DOCKER_IMAGE_NAME=your-registry/dealer-report
DOCKER_USER=your-docker-username
DOCKER_PASS=your-docker-password
```

### 2. Scheduled Workflow

The daily report runs at **07:30 UTC** (≈ 09:30 CEST) via CircleCI cron:

```yaml
schedule:
  cron: "30 7 * * *"  # 07:30 UTC ≈ 09:30 CEST
```

**Note**: This is one hour off during CET (winter). For precise 09:30 Europe/Paris, use two schedules:
- `30 8 * 11-3 *` (Nov-Mar: CET, UTC+1)
- `30 7 * 4-10 *` (Apr-Oct: CEST, UTC+2)

## Database Schema

### retailer_rules
```sql
retailer           VARCHAR(128) PRIMARY KEY
min_success_rate   FLOAT NULL          -- e.g., 0.95 for 95%
min_progress_0930  FLOAT NULL          -- e.g., 0.10 for 10%
include_successes  TINYINT(1) DEFAULT 0
```

### crawler_runs
```sql
id           BIGINT PRIMARY KEY AUTO_INCREMENT
retailer     VARCHAR(128) NOT NULL
planned_for  DATE NOT NULL           -- the day this run belongs to
started_at   DATETIME NOT NULL
finished_at  DATETIME NULL
status       ENUM('success','error','running','queued')
total_items  INT NULL
ok_items     INT NULL
ko_items     INT NULL
```

### runs_plan (optional)
```sql
plan_date      DATE NOT NULL
retailer       VARCHAR(128) NOT NULL
expected_total INT NOT NULL
PRIMARY KEY (plan_date, retailer)
```

## Development

### Run Tests

```bash
pip install -e .[test]
pytest -v
```

### Test Coverage

```bash
pytest --cov=cli --cov-report=html
open htmlcov/index.html
```

### Local Development

```bash
# Install in development mode
pip install -e .

# Run with local .env
dealer-report generate_dealer_report --fmt html

# Test with sample data
mysql -u root -p your_database < db/seed_data.sql
```

## Troubleshooting

### Database Connection Issues

```bash
# Test connection
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD $DB_NAME -e "SELECT 1"

# Check tables exist
mysql -h $DB_HOST -P $DB_PORT -u $DB_USER -p$DB_PASSWORD $DB_NAME -e "SHOW TABLES"
```

### GCS Authentication Issues

```bash
# Check default credentials
gcloud auth application-default print-access-token

# Set service account key
export GOOGLE_APPLICATION_CREDENTIALS=/path/to/service-account.json

# Test GCS access
gsutil ls gs://your-bucket-name
```

### Teams Webhook Issues

```bash
# Test webhook manually
curl -X POST "$TEAMS_WEBHOOK_URL" \
  -H "Content-Type: application/json" \
  -d '{"text": "Test message"}'

# Check webhook URL format
echo $TEAMS_WEBHOOK_URL | grep -E "https://.*\.webhook\.office\.com"
```

### Common Error Messages

| Error | Solution |
|-------|----------|
| `No module named 'cli'` | Run `pip install -e .` |
| `Access denied for user` | Check DB credentials in `.env` |
| `DefaultCredentialsError` | Set up GCS authentication |
| `Teams webhook returned 400` | Verify webhook URL format |
| `No such file or directory` | Check file paths are absolute |

### Timezone Issues

The application uses `Europe/Paris` timezone for 09:30 calculations. Verify:

```python
from zoneinfo import ZoneInfo
from datetime import datetime
tz = ZoneInfo('Europe/Paris')
now = datetime.now(tz)
print(f"Current time in Paris: {now}")
```

### Performance Tuning

For large datasets:
- Add database indexes on frequently queried columns
- Consider partitioning `crawler_runs` by date
- Use connection pooling for high-frequency runs
- Monitor GCS upload times and adjust timeout settings

## License

MIT License - see LICENSE file for details.

## Support

For issues and questions:
1. Check this README's troubleshooting section
2. Review CircleCI build logs
3. Check application logs for detailed error messages
4. Verify all environment variables are set correctly
