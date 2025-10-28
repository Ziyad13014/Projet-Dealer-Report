# Générer le token (ouvre Chrome, se connecte, récupère le token)
python scripts\get_spidervision_token.py

# Tester que le token fonctionne
python scripts\tester_token.py

# Créer le rapport HTML avec les 36 retailers
python src\generate_new_report.py

# OU tout en 1 clic
python scripts\lancer_rapport.bat

   # 1. Récupérer un nouveau token (si expiré)
   # Générer le token (ouvre Chrome, se connecte, récupère le token)
   python scripts\get_spidervision_token.py

   # 2. Générer le rapport
   # Créer le rapport HTML avec les 36 retailers
   python src\generate_new_report.py