#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Script pour vérifier les problèmes de sécurité potentiels dans le projet sadie.
Ce script vérifie :
 - Les secrets codés en dur
 - Les importations non sécurisées
 - Les vérifications SSL désactivées
 - Les vulnérabilités dans les dépendances
 - Les fichiers .env versionnés par erreur
"""

import os
import re
import glob
import sys
import subprocess
from pathlib import Path

# Chemins à exclure
EXCLUDE_DIRS = ['.git', '.venv', 'venv', 'node_modules', 'old', '__pycache__', 'build', 'dist']
EXCLUDE_FILES = ['security_check.py']

# Motifs pour détecter les secrets potentiels
SECRET_PATTERNS = [
    r'(?i)(?:api_key|apikey|secret|password|token|auth)(?:"|\'|\s*=\s*)["\']([^"\']+)["\']',
    r'(?i)(?:bearer\s+)["\']([a-zA-Z0-9_\-\.=]+)["\']',
    r'(?i)(?:jwt|access_token)["\']:\s*["\']([a-zA-Z0-9_\-\.=]+)["\']',
]

# Imports potentiellement non sécurisés
INSECURE_IMPORTS = [
    'pickle',
    'marshal',
    'shelve',
    'eval',
    'exec',
    'compile',
    'subprocess.call',
    'os.system',
    'os.popen',
    'telnetlib',
    'ftplib'
]

def check_hardcoded_secrets():
    """Vérifie les secrets codés en dur dans le code."""
    print("🔍 Vérification des secrets codés en dur...")
    
    # Liste pour stocker les correspondances trouvées
    found_secrets = []
    
    # Motifs à ignorer (variables, valeurs factices)
    ignore_patterns = [
        r'API_KEY',
        r'SECRET_KEY',
        r'YOUR_API_KEY',
        r'YOUR_SECRET',
        r'example',
        r'test',
        r'dummy',
        r'placeholder',
        r'xxx',
        r'<api_key>',
        r'\$\{.*\}',  # Variables d'environnement ${VAR}
        r'\{\{.*\}\}',  # Templates Jinja2 {{var}}
        r'os\.getenv',
        r'os\.environ',
        r'config\['
    ]

    # Recherche dans tous les fichiers Python et JavaScript/TypeScript
    for ext in ['py', 'js', 'ts', 'jsx', 'tsx']:
        for file_path in glob.glob(f'**/*.{ext}', recursive=True):
            # Ignorer les répertoires exclus
            if any(exclude_dir in file_path for exclude_dir in EXCLUDE_DIRS):
                continue
                
            # Ignorer les fichiers exclus
            if any(exclude_file in file_path for exclude_file in EXCLUDE_FILES):
                continue
            
            try:
                with open(file_path, 'r', encoding='utf-8') as file:
                    content = file.read()
                    
                    # Vérifier les secrets
                    for pattern in SECRET_PATTERNS:
                        matches = re.finditer(pattern, content)
                        for match in matches:
                            secret = match.group(1)
                            # Ignorer les faux positifs
                            if any(re.search(ignore, secret) for ignore in ignore_patterns):
                                continue
                            # Ignorer les secrets trop courts
                            if len(secret) < 8:
                                continue
                            found_secrets.append((file_path, secret))
            except Exception as e:
                print(f"⚠️ Erreur lors de la lecture de {file_path}: {str(e)}")
    
    if found_secrets:
        print(f"❌ Trouvé {len(found_secrets)} secrets potentiels codés en dur:")
        for file_path, secret in found_secrets:
            masked_secret = secret[:3] + '*' * (len(secret) - 6) + secret[-3:] if len(secret) > 6 else '***'
            print(f"  - {file_path}: {masked_secret}")
    else:
        print("✅ Aucun secret codé en dur n'a été trouvé.")
    
    return len(found_secrets)

def check_insecure_imports():
    """Vérifie les importations non sécurisées."""
    print("\n🔍 Vérification des importations non sécurisées...")
    
    # Liste pour stocker les importations non sécurisées trouvées
    found_imports = []
    
    # Recherche dans tous les fichiers Python
    for file_path in glob.glob('**/*.py', recursive=True):
        # Ignorer les répertoires exclus
        if any(exclude_dir in file_path for exclude_dir in EXCLUDE_DIRS):
            continue
            
        # Ignorer les fichiers exclus
        if any(exclude_file in file_path for exclude_file in EXCLUDE_FILES):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Vérifier les importations non sécurisées
                for insecure_import in INSECURE_IMPORTS:
                    # Vérifier les importations
                    if f'import {insecure_import}' in content or f'from {insecure_import}' in content:
                        found_imports.append((file_path, insecure_import))
                    # Vérifier les utilisations directes
                    elif f' {insecure_import}(' in content:
                        found_imports.append((file_path, insecure_import))
        except Exception as e:
            print(f"⚠️ Erreur lors de la lecture de {file_path}: {str(e)}")
    
    if found_imports:
        print(f"❌ Trouvé {len(found_imports)} importations potentiellement non sécurisées:")
        for file_path, insecure_import in found_imports:
            print(f"  - {file_path}: {insecure_import}")
    else:
        print("✅ Aucune importation non sécurisée n'a été trouvée.")
    
    return len(found_imports)

def check_verify_false():
    """Vérifie les appels HTTP avec verify=False."""
    print("\n🔍 Vérification des appels HTTP avec verify=False...")
    
    # Liste pour stocker les occurrences trouvées
    found_verify_false = []
    
    # Recherche dans tous les fichiers Python
    for file_path in glob.glob('**/*.py', recursive=True):
        # Ignorer les répertoires exclus
        if any(exclude_dir in file_path for exclude_dir in EXCLUDE_DIRS):
            continue
        
        try:
            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read()
                
                # Vérifier verify=False dans les appels HTTP
                if re.search(r'(?:requests|httpx|aiohttp).*verify\s*=\s*False', content):
                    found_verify_false.append(file_path)
        except Exception as e:
            print(f"⚠️ Erreur lors de la lecture de {file_path}: {str(e)}")
    
    if found_verify_false:
        print(f"❌ Trouvé {len(found_verify_false)} fichiers avec verify=False:")
        for file_path in found_verify_false:
            print(f"  - {file_path}")
    else:
        print("✅ Aucun appel HTTP avec verify=False n'a été trouvé.")
    
    return len(found_verify_false)

def check_dependency_vulnerabilities():
    """Vérifie les vulnérabilités dans les dépendances avec safety."""
    print("\n🔍 Vérification des vulnérabilités dans les dépendances...")
    
    # Vérifier si safety est installé
    try:
        subprocess.run(["safety", "--version"], capture_output=True, check=True)
    except (subprocess.CalledProcessError, FileNotFoundError):
        print("⚠️ L'outil safety n'est pas installé. Installez-le avec 'pip install safety'.")
        return 0
    
    # Vérifier si requirements.txt existe
    if not os.path.exists('requirements.txt'):
        print("⚠️ Fichier requirements.txt non trouvé.")
        return 0
    
    # Exécuter safety check
    try:
        result = subprocess.run(
            ["safety", "check", "-r", "requirements.txt", "--json"],
            capture_output=True,
            text=True
        )
        
        if result.returncode == 0:
            print("✅ Aucune vulnérabilité n'a été trouvée dans les dépendances.")
            return 0
        else:
            try:
                import json
                vulnerabilities = json.loads(result.stdout)
                count = len(vulnerabilities.get('vulnerabilities', []))
                print(f"❌ Trouvé {count} vulnérabilités dans les dépendances:")
                
                for vuln in vulnerabilities.get('vulnerabilities', []):
                    print(f"  - {vuln.get('package_name')}: {vuln.get('vulnerable_spec')}")
                    print(f"    ID: {vuln.get('vulnerability_id')}")
                    print(f"    Description: {vuln.get('advisory')}")
                    print(f"    Solution: Mettre à jour vers {vuln.get('fixed_version')}")
                    print()
                
                return count
            except json.JSONDecodeError:
                print("❌ Vulnérabilités trouvées, mais impossible de parser la sortie JSON.")
                print(result.stdout)
                return 1
    except Exception as e:
        print(f"⚠️ Erreur lors de l'exécution de safety: {str(e)}")
        return 0

def check_env_files():
    """Vérifie les fichiers .env versionnés par erreur."""
    print("\n🔍 Vérification des fichiers .env versionnés...")
    
    # Liste pour stocker les fichiers .env trouvés
    found_env_files = []
    
    # Recherche des fichiers .env
    for file_path in glob.glob('**/.env*', recursive=True):
        # Ignorer les fichiers .env.example et similaires
        if file_path.endswith('.example') or file_path.endswith('.template') or file_path.endswith('.sample'):
            continue
        found_env_files.append(file_path)
    
    if found_env_files:
        print(f"⚠️ Trouvé {len(found_env_files)} fichiers .env potentiellement versionnés par erreur:")
        for file_path in found_env_files:
            print(f"  - {file_path}")
    else:
        print("✅ Aucun fichier .env n'a été trouvé.")
    
    return len(found_env_files)

def main():
    """Fonction principale."""
    print("=" * 80)
    print("🔒 Début des vérifications de sécurité pour sadie...\n")
    print("=" * 80)
    
    # Exécuter toutes les vérifications
    issues_count = 0
    
    issues_count += check_hardcoded_secrets()
    issues_count += check_insecure_imports()
    issues_count += check_verify_false()
    issues_count += check_dependency_vulnerabilities()
    issues_count += check_env_files()
    
    # Résumé
    print("\n" + "=" * 80)
    if issues_count == 0:
        print("✅ FÉLICITATIONS : Aucun problème de sécurité détecté!")
        sys.exit(0)
    else:
        print(f"❌ ATTENTION : {issues_count} problèmes de sécurité potentiels détectés!")
        sys.exit(1)

if __name__ == "__main__":
    main() 