#!/usr/bin/env python3
"""
Script de test pour vérifier le système de seuils personnalisés
"""

import json
from analyze_live_api import get_retailer_thresholds, get_status_for_retailer

def test_classification_system():
    """Test du système de classification avec des exemples"""
    print("🧪 TEST DU SYSTÈME DE CLASSIFICATION PERSONNALISÉ")
    print("=" * 60)
    
    # Récupérer les seuils
    thresholds = get_retailer_thresholds()
    
    # Tests avec des exemples concrets
    test_cases = [
        {
            "retailer": "Auchan Livraison",
            "test_values": [98.0, 96.5, 94.5, 91.0, 89.0]
        },
        {
            "retailer": "CollectAndGo", 
            "test_values": [90.0, 85.0, 82.0, 80.0, 75.0]
        },
        {
            "retailer": "Intermarché",
            "test_values": [100.0, 99.9, 96.0, 94.0, 90.0]
        }
    ]
    
    for test in test_cases:
        retailer = test["retailer"]
        success_threshold = thresholds[retailer]["success_min"]
        
        print(f"\n🏪 {retailer}")
        print(f"   Seuil de succès: {success_threshold}%")
        print(f"   Zones: Succès ≥{success_threshold}%, Warning {success_threshold-5}%-{success_threshold}%, Erreur <{success_threshold-5}%")
        print("   " + "-" * 50)
        
        for value in test["test_values"]:
            status = get_status_for_retailer(value, success_threshold)
            
            if status == "Succès":
                emoji = "✅"
            elif status == "Warning":
                emoji = "⚠️"
            else:
                emoji = "❌"
                
            print(f"   {emoji} {value:5.1f}% → {status}")
    
    print("\n" + "=" * 60)
    print("📊 RÉSUMÉ DES SEUILS PAR ENSEIGNE")
    print("=" * 60)
    
    # Afficher tous les seuils
    for retailer, data in sorted(thresholds.items()):
        if data["success_min"] is not None:
            success_min = data["success_min"]
            warning_zone = f"{success_min-5:.1f}%-{success_min:.1f}%"
            print(f"{retailer:<20} | Succès: ≥{success_min:5.1f}% | Warning: {warning_zone} | Erreur: <{success_min-5:.1f}%")
        else:
            print(f"{retailer:<20} | N/A")

if __name__ == "__main__":
    test_classification_system()
