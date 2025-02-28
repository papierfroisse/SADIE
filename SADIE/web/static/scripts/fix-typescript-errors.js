#!/usr/bin/env node

/**
 * Script de correction automatique des erreurs TypeScript courantes
 * Pour SADIE Dashboard
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Couleurs pour la console
const colors = {
  reset: '\x1b[0m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  red: '\x1b[31m',
  blue: '\x1b[34m',
  cyan: '\x1b[36m',
  magenta: '\x1b[35m',
  bold: '\x1b[1m'
};

// Configuration
const ROOT_DIR = path.resolve(__dirname, '..');
const SRC_DIR = path.join(ROOT_DIR, 'src');
const TYPES_FILE = path.join(SRC_DIR, 'types', 'index.ts');

console.log(`${colors.magenta}${colors.bold}Correction automatique des erreurs TypeScript - SADIE Dashboard${colors.reset}\n`);

// Corrections connues à appliquer
const knownFixes = [
  {
    description: 'Correction des propriétés notification_type en notificationType',
    apply: () => {
      const files = [
        path.join(SRC_DIR, 'components', 'AlertList.tsx'),
        path.join(SRC_DIR, 'components', 'trading', 'AlertPanel.tsx')
      ];
      
      files.forEach(file => {
        if (!fs.existsSync(file)) {
          console.log(`${colors.yellow}Le fichier ${file} n'existe pas, ignoré${colors.reset}`);
          return;
        }
        
        let content = fs.readFileSync(file, 'utf8');
        const original = content;
        
        // Remplacer notification_type par notificationType
        content = content.replace(/notification_type/g, 'notificationType');
        
        if (content !== original) {
          fs.writeFileSync(file, content);
          console.log(`${colors.green}✓ Correction appliquée à ${file}${colors.reset}`);
        } else {
          console.log(`${colors.blue}Aucune correction nécessaire pour ${file}${colors.reset}`);
        }
      });
    }
  },
  {
    description: 'Ajout des types manquants et correction de sizeMap dans Dashboard',
    apply: () => {
      const dashboardFile = path.join(SRC_DIR, 'pages', 'Dashboard.tsx');
      
      if (!fs.existsSync(dashboardFile)) {
        console.log(`${colors.yellow}Le fichier ${dashboardFile} n'existe pas, ignoré${colors.reset}`);
        return;
      }
      
      let content = fs.readFileSync(dashboardFile, 'utf8');
      
      // Vérifier si sizeMap est déjà défini
      if (!content.includes('const sizeMap =')) {
        // Trouver un bon endroit pour insérer sizeMap (après les définitions d'interface ou imports)
        const insertionPoint = content.indexOf('const Dashboard') !== -1 
          ? content.indexOf('const Dashboard')
          : content.indexOf('interface') !== -1 
            ? content.indexOf('interface') 
            : content.indexOf('import');
        
        // Définir sizeMap
        const sizeMapDefinition = `
// Carte de taille pour les widgets
const sizeMap = {
  small: 4,  // 1/3 de la ligne
  medium: 6, // 1/2 de la ligne
  large: 12  // Largeur complète
};

`;
        
        // Insérer la définition
        content = content.slice(0, insertionPoint) + sizeMapDefinition + content.slice(insertionPoint);
        
        fs.writeFileSync(dashboardFile, content);
        console.log(`${colors.green}✓ sizeMap ajouté à ${dashboardFile}${colors.reset}`);
      } else {
        console.log(`${colors.blue}sizeMap est déjà défini dans ${dashboardFile}${colors.reset}`);
      }
    }
  },
  {
    description: 'Correction des imports pour les types dans services/api.ts',
    apply: () => {
      const apiFile = path.join(SRC_DIR, 'services', 'api.ts');
      
      if (!fs.existsSync(apiFile)) {
        console.log(`${colors.yellow}Le fichier ${apiFile} n'existe pas, ignoré${colors.reset}`);
        return;
      }
      
      let content = fs.readFileSync(apiFile, 'utf8');
      const original = content;
      
      // Remplacer les imports
      content = content.replace(
        /import (.*) from '\.\.\/types';/,
        "import { MarketData, Alert, ApiResponse } from '../types';\n// Ajouté par le script de correction\nexport interface Trade {\n  type: 'trade';\n  id: string;\n  symbol: string;\n  price: number;\n  quantity: number;\n  side: 'buy' | 'sell';\n  timestamp: number;\n};"
      );
      
      // Ajouter l'export de la classe ApiService
      content = content.replace(
        /class ApiService {/,
        "export default class ApiService {"
      );
      
      if (content !== original) {
        fs.writeFileSync(apiFile, content);
        console.log(`${colors.green}✓ Correction des imports dans ${apiFile}${colors.reset}`);
      } else {
        console.log(`${colors.blue}Aucune correction nécessaire pour ${apiFile}${colors.reset}`);
      }
    }
  }
];

// Exécution des corrections
console.log(`${colors.cyan}Exécution des corrections connues...${colors.reset}\n`);
knownFixes.forEach(fix => {
  console.log(`${colors.bold}${fix.description}${colors.reset}`);
  try {
    fix.apply();
    console.log('');
  } catch (error) {
    console.error(`${colors.red}Erreur: ${error.message}${colors.reset}\n`);
  }
});

// Vérification du résultat avec tsc
try {
  console.log(`${colors.cyan}Vérification du résultat avec TypeScript...${colors.reset}`);
  execSync('npx tsc --noEmit', { stdio: 'pipe', cwd: ROOT_DIR });
  console.log(`${colors.green}${colors.bold}✓ Vérification TypeScript réussie!${colors.reset}`);
} catch (error) {
  console.log(`${colors.yellow}Des erreurs TypeScript subsistent:${colors.reset}`);
  console.log(error.stdout.toString());
  console.log(`\n${colors.yellow}Exécutez "npm run type-check:report" pour plus de détails${colors.reset}`);
}

console.log(`\n${colors.magenta}${colors.bold}Correction terminée. Veuillez redémarrer le serveur de développement pour appliquer les changements.${colors.reset}`); 