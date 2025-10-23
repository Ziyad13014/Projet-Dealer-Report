import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv
import os

load_dotenv()

from cli.services.auth import SpiderVisionAuth
auth = SpiderVisionAuth()
token = auth.login()
print("✅ Authentifié")

base_url = os.getenv("SPIDER_VISION_API_BASE")
page_url = f"{base_url.replace('food-api-', '')}/store-history"

headers = {"Authorization": f"Bearer {token}", "User-Agent": "Mozilla/5.0"}

print(f"🔄 Scraping {page_url}...")
response = requests.get(page_url, headers=headers, timeout=30)

soup = BeautifulSoup(response.text, "html.parser")
table = soup.find("table")

if table:
    headers_row = table.find("thead").find("tr") if table.find("thead") else table.find("tr")
    headers = [th.get_text().strip() for th in headers_row.find_all(["th", "td"])]
    print(f"📋 Colonnes: {headers}")
    
    # Chercher l'index de Last day history
    try:
        idx = headers.index("Last day history")
        print(f"✅ Colonne trouvée à l'index {idx}")
        
        rows = table.find("tbody").find_all("tr") if table.find("tbody") else table.find_all("tr")[1:]
        for row in rows[:3]:
            cells = row.find_all(["td", "th"])
            if len(cells) > idx:
                print(f"{cells[0].get_text().strip()}: {cells[idx].get_text().strip()}")
    except ValueError:
        print(f"❌ Colonne 'Last day history' non trouvée. Colonnes: {headers}")
else:
    print("❌ Tableau non trouvé")
