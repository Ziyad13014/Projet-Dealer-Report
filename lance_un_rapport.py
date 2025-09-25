#!/usr/bin/env python3
"""
Lance rapidement la génération d'un rapport HTML (version sans bouton Détail).

Utilisation:
    python lance_un_rapport.py

Ce script est un simple alias qui appelle generate_new_report.py pour
produire un fichier HTML dans le dossier reports/ avec un horodatage.
"""
from generate_new_report import generate_new_report as main

if __name__ == "__main__":
    main()
