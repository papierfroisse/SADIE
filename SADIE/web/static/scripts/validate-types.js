#!/usr/bin/env node

/**
 * Script de validation TypeScript qui exécute la vérification des types
 * et génère un rapport détaillé des erreurs.
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

const REPORT_DIR = path.join(__dirname, '..', 'reports');
const REPORT_PATH = path.join(REPORT_DIR, 'typescript-report.json');

// Créer le dossier de rapports s'il n'existe pas
if (!fs.existsSync(REPORT_DIR)) {
  fs.mkdirSync(REPORT_DIR, { recursive: true });
}

// Classes de couleurs pour l'affichage console
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
  bold: '\x1b[1m',
};

console.log(`${colors.cyan}${colors.bold}Exécution de la vérification TypeScript...${colors.reset}`);

// Exécuter tsc pour vérifier les types
const tsc = spawn('npx', ['tsc', '--noEmit', '--pretty', 'false']);

let output = '';
let errors = [];

tsc.stdout.on('data', (data) => {
  output += data.toString();
});

tsc.stderr.on('data', (data) => {
  output += data.toString();
});

tsc.on('close', (code) => {
  // Analyser la sortie pour extraire les erreurs
  const errorLines = output.split('\n').filter(line => line.trim() !== '');
  
  // Grouper les erreurs par fichier
  const errorsByFile = {};
  
  errorLines.forEach(line => {
    // Format d'erreur TypeScript: fichier(ligne,colonne): erreur TS1234: message
    const match = line.match(/(.+)\((\d+),(\d+)\):\s+(.+)/);
    if (match) {
      const [, filePath, lineNum, colNum, errorMessage] = match;
      const fileName = path.basename(filePath);
      
      if (!errorsByFile[fileName]) {
        errorsByFile[fileName] = [];
      }
      
      errorsByFile[fileName].push({
        file: filePath,
        line: parseInt(lineNum, 10),
        column: parseInt(colNum, 10),
        message: errorMessage,
      });
      
      errors.push({
        file: filePath,
        line: parseInt(lineNum, 10),
        column: parseInt(colNum, 10),
        message: errorMessage,
      });
    }
  });
  
  // Générer le rapport
  const report = {
    timestamp: new Date().toISOString(),
    totalErrors: errors.length,
    errorsByFile,
    errors,
  };
  
  fs.writeFileSync(REPORT_PATH, JSON.stringify(report, null, 2));
  
  // Afficher le résumé
  if (errors.length > 0) {
    console.log(`${colors.red}${colors.bold}✘ Échec de la vérification TypeScript${colors.reset}`);
    console.log(`${colors.yellow}Total des erreurs: ${errors.length}${colors.reset}`);
    
    Object.keys(errorsByFile).forEach(file => {
      console.log(`\n${colors.magenta}${file}${colors.reset} - ${errorsByFile[file].length} erreurs`);
      
      // Afficher les 3 premières erreurs par fichier
      errorsByFile[file].slice(0, 3).forEach(error => {
        console.log(`  ${colors.yellow}Ligne ${error.line}:${error.column}${colors.reset} - ${error.message}`);
      });
      
      if (errorsByFile[file].length > 3) {
        console.log(`  ${colors.cyan}... et ${errorsByFile[file].length - 3} autres erreurs${colors.reset}`);
      }
    });
    
    console.log(`\n${colors.blue}Rapport détaillé sauvegardé dans:${colors.reset} ${REPORT_PATH}`);
    console.log(`${colors.green}Exécutez ${colors.bold}npm run fix-all${colors.reset}${colors.green} pour tenter de corriger les problèmes automatiquement.${colors.reset}`);
    
    process.exit(1);
  } else {
    console.log(`${colors.green}${colors.bold}✓ Vérification TypeScript réussie !${colors.reset}`);
    process.exit(0);
  }
}); 