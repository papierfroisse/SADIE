rite-Host "Optimisation du Dockerfile frontend..." -ForegroundColor Cyan

# Vérification de l'emplacement du Dockerfile
$dockerfilePath = "sadie/web/static/Dockerfile"
if (Test-Path $dockerfilePath) {
    # Sauvegarde du Dockerfile original
    Copy-Item $dockerfilePath "$dockerfilePath.bak"
    Write-Host "Dockerfile original sauvegardé dans $dockerfilePath.bak" -ForegroundColor Green
} else {
    Write-Host "Aucun Dockerfile existant trouvé. Création d'un nouveau..." -ForegroundColor Yellow
}

# Création du nouveau Dockerfile optimisé
$newDockerfileContent = @"
FROM node:16-alpine

WORKDIR /app/sadie/web/static

# Installation de cross-env pour les variables d'environnement
RUN npm install -g cross-env

# Copie des fichiers de configuration
COPY package*.json ./

# Installation des dépendances
RUN npm install

# Copie du code source
COPY . .

# Configuration pour éviter les problèmes de mémoire
ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV GENERATE_SOURCEMAP=false

# Configuration du port
EXPOSE 3000

# Commande de démarrage optimisée
CMD ["npm", "run", "start:safe"]
"@

# Écriture du nouveau Dockerfile
Set-Content $dockerfilePath $newDockerfileContent
Write-Host "Nouveau Dockerfile optimisé créé avec succès!" -ForegroundColor Green

# Affichage des instructions suivantes
Write-Host "`nÉtapes suivantes:" -ForegroundColor Cyan
Write-Host "1. Mettez à jour le package.json avec le script restart-sadie-frontend.ps1" -ForegroundColor Yellow
Write-Host "2. Reconstruisez l'image avec: docker-compose build frontend" -ForegroundColor Yellow
Write-Host "3. Redémarrez le conteneur avec: ./restart-sadie-frontend.ps1" -ForegroundColor Yellow
