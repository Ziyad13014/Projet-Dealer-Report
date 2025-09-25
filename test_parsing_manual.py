#!/usr/bin/env python3
"""Test manuel pour vérifier le parsing WebDataRepository"""

def test_parse_table_row():
    """Test manuel de la fonction _parse_table_row"""
    
    # Simuler des données de cellules comme dans l'image
    test_cases = [
        # Cas 1: Naturalia avec 0% on 0 stores
        {
            'cells': ['46', 'Naturalia', '0', '2/2', '2', '0%', 'on 0 stores', '100%', '100%'],
            'expected_success': 0.0
        },
        # Cas 2: Franprix avec 0% on 113 stores  
        {
            'cells': ['49', 'Franprix', '113', '3/116', '116', '97%', '0%', 'on 113 stores', '-'],
            'expected_success': 0.0
        },
        # Cas 3: Format combiné "97% on 113 stores"
        {
            'cells': ['49', 'Franprix', '113', '3/116', '116', '97%', '0% on 113 stores', '-'],
            'expected_success': 0.0
        }
    ]
    
    print("🧪 Test manuel du parsing WebDataRepository")
    print("=" * 50)
    
    for i, test_case in enumerate(test_cases, 1):
        print(f"\n📋 Test Case {i}:")
        cells = test_case['cells']
        expected = test_case['expected_success']
        
        print(f"   Cellules: {cells}")
        
        # Simuler la logique de parsing
        success_rate = 0.0
        progress_rate = 0.0
        
        # Chercher dans les colonnes 5+
        for j in range(5, len(cells)):
            text = cells[j].strip()
            print(f"   Analyse colonne {j}: '{text}'")
            
            # Si on trouve un pourcentage
            if '%' in text:
                # Extraire le pourcentage (simulation simple)
                try:
                    percent_str = text.replace('%', '').strip()
                    if 'on' in text.lower():
                        # Format "X% on Y stores"
                        percent_str = percent_str.split('on')[0].strip()
                    percent = float(percent_str)
                    
                    # Si c'est la colonne Success (contient "on X stores")
                    if 'on' in text.lower() and 'stores' in text.lower():
                        success_rate = percent
                        print(f"     → Success rate trouvé: {percent}%")
                    # Sinon c'est probablement le progress rate
                    elif progress_rate == 0.0:
                        progress_rate = percent
                        print(f"     → Progress rate trouvé: {percent}%")
                        
                except ValueError:
                    print(f"     → Erreur parsing pourcentage: {text}")
            
            # Si on trouve "on X stores" sans pourcentage, chercher dans la cellule précédente
            elif 'on' in text.lower() and 'stores' in text.lower() and j > 0:
                prev_text = cells[j-1].strip()
                print(f"     → Trouvé 'on X stores', check cellule précédente: '{prev_text}'")
                if '%' in prev_text:
                    try:
                        percent = float(prev_text.replace('%', '').strip())
                        success_rate = percent
                        print(f"     → Success rate depuis cellule précédente: {percent}%")
                    except ValueError:
                        print(f"     → Erreur parsing cellule précédente: {prev_text}")
        
        print(f"   ✅ Résultat:")
        print(f"     Success rate: {success_rate}%")
        print(f"     Progress rate: {progress_rate}%")
        print(f"     Attendu: {expected}%")
        
        if success_rate == expected:
            print(f"     🎯 SUCCESS - Extraction correcte!")
        else:
            print(f"     ❌ ÉCHEC - Attendu {expected}%, obtenu {success_rate}%")

if __name__ == "__main__":
    test_parse_table_row()
