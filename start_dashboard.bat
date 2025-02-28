@echo off
echo ======================================
echo SADIE Dashboard - Experience
echo ======================================
echo.

REM Vérifier si Python est installé
python --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Python n'est pas installé ou n'est pas dans le PATH.
    echo Veuillez installer Python depuis https://www.python.org/downloads/
    pause
    exit /b 1
)

REM Vérifier si Node.js est installé
node --version > nul 2>&1
if %errorlevel% neq 0 (
    echo Node.js n'est pas installé ou n'est pas dans le PATH.
    echo Veuillez installer Node.js depuis https://nodejs.org/
    pause
    exit /b 1
)

REM Installer les dépendances Python nécessaires
echo Installation des dépendances Python...
pip install fastapi uvicorn python-multipart > nul 2>&1

REM Démarrer le serveur backend en arrière-plan
echo Démarrage du serveur backend...
start cmd /k python sadie/web/mock_api.py

REM Attendre 2 secondes pour que le serveur démarre
timeout /t 2 > nul

REM Se déplacer dans le répertoire frontend
cd sadie/web/static

REM Installer les dépendances npm si nécessaire
echo Installation des dépendances npm...
if not exist "node_modules" (
    npm install
)

REM Créer un fichier .env pour configurer l'API_URL
echo REACT_APP_API_URL=http://localhost:8000 > .env

REM Démarrer l'application React
echo Démarrage de l'application frontend...
start cmd /k npm start

echo.
echo ======================================
echo Le dashboard va s'ouvrir dans votre navigateur...
echo Utilisez les identifiants suivants pour vous connecter:
echo   Nom d'utilisateur: testuser
echo   Mot de passe: password123
echo ======================================

REM Ouvrir le navigateur après 5 secondes
timeout /t 5 > nul
start http://localhost:3000

echo.
echo Pour arrêter l'application, fermez les fenêtres de terminal.
echo ====================================== 