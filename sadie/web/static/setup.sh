#!/bin/bash

# Couleurs pour les messages
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

echo -e "${YELLOW}Installation de l'environnement de développement SADIE Frontend...${NC}\n"

# Vérification de Node.js
if ! command -v node &> /dev/null; then
    echo "Node.js n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

# Vérification de npm
if ! command -v npm &> /dev/null; then
    echo "npm n'est pas installé. Veuillez l'installer d'abord."
    exit 1
fi

echo -e "${GREEN}Nettoyage des installations précédentes...${NC}"
rm -rf node_modules
rm -f package-lock.json

echo -e "${GREEN}Installation des dépendances...${NC}"
npm install

echo -e "${GREEN}Vérification des types...${NC}"
npm run type-check

echo -e "${GREEN}Vérification du linting...${NC}"
npm run lint

echo -e "${GREEN}Formatage du code...${NC}"
npm run format

echo -e "\n${GREEN}Installation terminée avec succès!${NC}"
echo -e "Pour démarrer l'application en développement:"
echo -e "  ${YELLOW}npm start${NC}"
echo -e "\nPour construire l'application pour la production:"
echo -e "  ${YELLOW}npm run build${NC}" 