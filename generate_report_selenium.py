#!/usr/bin/env python3
"""Génère un rapport en utilisant Selenium pour scraper SpiderVision"""

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
from dotenv import load_dotenv
import os
import time

load_dotenv()

def scrape_with_selenium():
    """Scrape SpiderVision avec Selenium (attend que JavaScript charge les données)"""
    
    print("🔄 Démarrage de Selenium...")
    
    # Configuration du navigateur
    options = webdriver.ChromeOptions()
    options.add_argument('--headless')  # Mode sans interface
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    
    # Démarrer le navigateur
    driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=options)
    
    try:
        # Authentification
        from cli.services.auth import SpiderVisionAuth
        auth = SpiderVisionAuth()
        token = auth.login()
        print("✅ Token obtenu")
        
        # Aller sur la page
        url = 'https://spider-vision.data-solutions.com'
        print(f"🌐 Chargement de {url}...")
        
        driver.get(url)
        
        # Essayer plusieurs méthodes pour injecter le token
        print("🔐 Injection du token...")
        driver.execute_script(f"""
            localStorage.setItem('token', '{token}');
            localStorage.setItem('authToken', '{token}');
            localStorage.setItem('jwt', '{token}');
            localStorage.setItem('access_token', '{token}');
            sessionStorage.setItem('token', '{token}');
            sessionStorage.setItem('authToken', '{token}');
        """)
        
        # Recharger la page pour que le token soit pris en compte
        print("🔄 Rechargement de la page...")
        driver.refresh()
        
        # Attendre un peu que la page se charge
        time.sleep(3)
        
        # Attendre que le tableau se charge (max 30 secondes)
        print("⏳ Attente du chargement du tableau...")
        wait = WebDriverWait(driver, 30)
        table = wait.until(EC.presence_of_element_located((By.TAG_NAME, "table")))
        
        print("✅ Tableau trouvé !")
        
        # Attendre que les données se chargent dans le tableau (attendre les lignes)
        print("⏳ Attente du chargement des données...")
        time.sleep(8)  # Attendre 8 secondes pour que JavaScript charge les données
        print("✅ Données chargées !")
        
        # Re-trouver le tableau pour éviter stale element
        table = driver.find_element(By.TAG_NAME, "table")
        
        # Extraire les données
        headers = []
        header_row = table.find_element(By.TAG_NAME, "thead").find_element(By.TAG_NAME, "tr")
        for th in header_row.find_elements(By.TAG_NAME, "th"):
            headers.append(th.text.strip())
        
        print(f"📋 Colonnes: {headers}")
        
        # Extraire les lignes
        retailers_data = []
        tbody = table.find_element(By.TAG_NAME, "tbody")
        rows = tbody.find_elements(By.TAG_NAME, "tr")
        
        print(f"📊 Nombre de lignes trouvées: {len(rows)}")
        
        for row in rows:
            cells = row.find_elements(By.TAG_NAME, "td")
            if len(cells) >= 3:
                retailer_data = {}
                for i, cell in enumerate(cells):
                    if i < len(headers):
                        retailer_data[headers[i]] = cell.text.strip()
                retailers_data.append(retailer_data)
        
        print(f"✅ {len(retailers_data)} enseignes récupérées")
        
        # Afficher un exemple
        if retailers_data:
            print(f"\n📊 Exemple (première enseigne):")
            for key, value in list(retailers_data[0].items())[:5]:
                print(f"  {key}: {value}")
        
        return retailers_data
        
    except Exception as e:
        print(f"❌ Erreur: {e}")
        import traceback
        traceback.print_exc()
        return None
        
    finally:
        driver.quit()
        print("🔚 Navigateur fermé")

if __name__ == "__main__":
    data = scrape_with_selenium()
    if data:
        print(f"\n🎉 Succès ! {len(data)} enseignes récupérées avec Selenium")