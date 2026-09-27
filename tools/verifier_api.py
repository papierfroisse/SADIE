"""Contrôle de l'API SADIE sans démarrer de serveur ni de base de données.

    .venv\\Scripts\\python.exe tools\\verifier_api.py

L'application est interrogée en mémoire (starlette TestClient) : on vérifie
que le paquet s'importe, que les routes sont montées et que les points
d'entrée publics répondent.
"""
import sys
from pathlib import Path

# Le script vit dans tools/ : sans cela, Python n'ajoute que tools/ à sys.path
# et `import sadie` échoue depuis un environnement virtuel.
RACINE = Path(__file__).resolve().parent.parent
if str(RACINE) not in sys.path:
    sys.path.insert(0, str(RACINE))

# La console Windows peut être en cp1252 : on force l'UTF-8 pour la sortie.
try:
    sys.stdout.reconfigure(encoding='utf-8')
except Exception:
    pass

ENDPOINTS = [
    '/api/healthcheck',
    '/api/endpoints',
    '/api/market/symbols',
]

try:
    from fastapi.testclient import TestClient
except ImportError:  # pragma: no cover
    print('  ! httpx/TestClient indisponible : installer httpx.')
    sys.exit(2)

try:
    from sadie.web.app import app
except Exception as err:
    print('  ECHEC : application non importable -> ' + repr(err))
    sys.exit(1)

print(f'  application   : {getattr(app, "title", "?")}')
routes = [r.path for r in app.routes if hasattr(r, 'methods')]
print(f'  routes montées : {len(routes)}')

client = TestClient(app, raise_server_exceptions=False)
echecs = 0
for chemin in ENDPOINTS:
    if chemin not in routes:
        print(f'  - {chemin} : absent (route non montée)')
        continue
    try:
        reponse = client.get(chemin)
    except Exception as err:
        print(f'  ECHEC {chemin} : {type(err).__name__} - {err}')
        echecs += 1
        continue
    etat = 'OK  ' if reponse.status_code < 500 else 'ECHEC'
    if reponse.status_code >= 500:
        echecs += 1
    print(f'  {etat} {chemin} : HTTP {reponse.status_code}')

if echecs:
    print(f'\n  {echecs} point(s) d\'entree en erreur.')
    sys.exit(1)
print('\n  OK : API operationnelle (application importable, points d\'entree joignables).')