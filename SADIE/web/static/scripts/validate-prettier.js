const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Définition des chemins
const REPORT_DIR = '../reports';
const REPORT_FILE = path.join(REPORT_DIR, 'prettier-report.json');

// Création du répertoire de rapport s'il n'existe pas
if (!fs.existsSync(REPORT_DIR)) {
  fs.mkdirSync(REPORT_DIR, { recursive: true });
}

// Couleurs pour la console
const colors = {
  reset: '\x1b[0m',
  red: '\x1b[31m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  white: '\x1b[37m',
};

console.log(`${colors.cyan}=========================================${colors.reset}`);
console.log(`${colors.cyan}    Validation Prettier en cours...     ${colors.reset}`);
console.log(`${colors.cyan}=========================================${colors.reset}`);

try {
  // Exécuter Prettier pour vérifier les fichiers non formatés
  const output = execSync(
    'npx prettier --check "src/**/*.{js,jsx,ts,tsx,json,css,scss,md}" --ignore-path .prettierignore',
    { encoding: 'utf-8', stdio: 'pipe' }
  ).toString();

  // Si nous arrivons ici, tout est correctement formaté
  console.log(`${colors.green}✓ Tous les fichiers sont correctement formatés selon les règles Prettier.${colors.reset}`);
} catch (error) {
  const errorOutput = error.stdout || error.message;
  
  // Analyser la sortie pour obtenir la liste des fichiers non formatés
  const unformattedFiles = errorOutput
    .split('\n')
    .filter(line => line.includes('[warn]'))
    .map(line => {
      const match = line.match(/\[warn\] (.+)/);
      return match ? match[1].trim() : null;
    })
    .filter(Boolean);
  
  // Créer un rapport au format JSON
  const report = {
    timestamp: new Date().toISOString(),
    totalUnformatted: unformattedFiles.length,
    unformattedFiles: unformattedFiles
  };
  
  // Sauvegarder le rapport
  fs.writeFileSync(REPORT_FILE, JSON.stringify(report, null, 2));
  
  console.log(`${colors.yellow}Résumé des problèmes de formatage:${colors.reset}`);
  console.log(`${colors.white}• Total des fichiers mal formatés: ${colors.red}${unformattedFiles.length}${colors.reset}`);
  
  // Afficher les 10 premiers fichiers non formatés
  if (unformattedFiles.length > 0) {
    console.log(`\n${colors.yellow}Fichiers nécessitant un formatage (10 premiers):${colors.reset}`);
    
    unformattedFiles.slice(0, 10).forEach((file, index) => {
      console.log(`${colors.white}${index + 1}. ${file}${colors.reset}`);
    });
    
    if (unformattedFiles.length > 10) {
      console.log(`${colors.white}... et ${unformattedFiles.length - 10} autres fichiers${colors.reset}`);
    }
    
    console.log(`\n${colors.yellow}Rapport complet sauvegardé dans: ${colors.reset}${colors.white}${REPORT_FILE}${colors.reset}`);
    console.log(`\n${colors.green}Pour corriger automatiquement les problèmes de formatage:${colors.reset}`);
    console.log(`${colors.white}npx prettier --write "src/**/*.{js,jsx,ts,tsx,json,css,scss,md}" --ignore-path .prettierignore${colors.reset}`);
    
    process.exit(1); // Sortie avec un code d'erreur
  }
} catch (generalError) {
  console.error(`${colors.red}Erreur lors de l'exécution de Prettier:${colors.reset}`);
  console.error(generalError.message || generalError);
  process.exit(1);
} 