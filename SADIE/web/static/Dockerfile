FROM node:16-alpine

WORKDIR /app/sadie/web/static

# Installation de cross-env pour les variables d'environnement
RUN npm install -g cross-env

# Copie des fichiers de configuration
COPY package*.json ./

# Installation des d�pendances
RUN npm install

# Copie du code source
COPY . .

# Configuration pour �viter les probl�mes de m�moire
ENV NODE_OPTIONS="--max-old-space-size=4096"
ENV GENERATE_SOURCEMAP=false

# Configuration du port
EXPOSE 3000

# Commande de d�marrage optimis�e
CMD ["npm", "run", "start:safe"]
