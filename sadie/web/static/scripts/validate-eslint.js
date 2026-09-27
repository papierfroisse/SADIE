const { execSync } = require('child_process');
const fs = require('fs');
const path = require('path');

// Définition des chemins
const REPORT_DIR = '../reports';
const REPORT_FILE = path.join(REPORT_DIR, 'eslint-report.json');

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
console.log(`${colors.cyan}     Validation ESLint en cours...      ${colors.reset}`);
console.log(`${colors.cyan}=========================================${colors.reset}`);

try {
  // Exécuter ESLint avec format JSON
  execSync('npx eslint --ext .js,.jsx,.ts,.tsx src --format json > ' + REPORT_FILE, {
    encoding: 'utf-8',
    stdio: 'pipe',
  });

  // Lire le rapport généré
  const report = JSON.parse(fs.readFileSync(REPORT_FILE, 'utf-8'));
  
  // Calculer les statistiques
  let totalErrors = 0;
  let totalWarnings = 0;
  let filesWithIssues = 0;
  
  report.forEach(file => {
    if (file.errorCount > 0 || file.warningCount > 0) {
      filesWithIssues++;
      totalErrors += file.errorCount;
      totalWarnings += file.warningCount;
    }
  });
  
  if (totalErrors > 0 || totalWarnings > 0) {
    console.log(`${colors.yellow}Résumé des problèmes ESLint:${colors.reset}`);
    console.log(`${colors.white}• Total des fichiers avec problèmes: ${colors.red}${filesWithIssues}${colors.reset}`);
    console.log(`${colors.white}• Erreurs: ${colors.red}${totalErrors}${colors.reset}`);
    console.log(`${colors.white}• Avertissements: ${colors.yellow}${totalWarnings}${colors.reset}`);
    
    // Afficher les détails des 5 fichiers avec le plus de problèmes
    const topIssueFiles = [...report]
      .filter(file => file.errorCount + file.warningCount > 0)
      .sort((a, b) => 
        (b.errorCount + b.warningCount) - (a.errorCount + a.warningCount)
      )
      .slice(0, 5);
    
    console.log(`\n${colors.yellow}Top 5 des fichiers problématiques:${colors.reset}`);
    
    topIssueFiles.forEach((file, index) => {
      console.log(`\n${colors.white}${index + 1}. ${file.filePath.split('src/')[1] || file.filePath}${colors.reset}`);
      console.log(`   Erreurs: ${colors.red}${file.errorCount}${colors.reset}, Avertissements: ${colors.yellow}${file.warningCount}${colors.reset}`);
      
      // Afficher les 3 premiers messages pour chaque fichier
      const topMessages = file.messages.slice(0, 3);
      if (topMessages.length > 0) {
        console.log(`   ${colors.white}Exemples de problèmes:${colors.reset}`);
        topMessages.forEach(msg => {
          const severity = msg.severity === 2 ? colors.red + '✘' : colors.yellow + '⚠';
          console.log(`   ${severity} ${colors.white}Ligne ${msg.line}:${msg.column}: ${colors.reset}${msg.message} ${colors.magenta}(${msg.ruleId})${colors.reset}`);
        });
        
        if (file.messages.length > 3) {
          console.log(`   ${colors.white}... et ${file.messages.length - 3} autres problèmes${colors.reset}`);
        }
      }
    });
    
    console.log(`\n${colors.yellow}Rapport complet sauvegardé dans: ${colors.reset}${colors.white}${REPORT_FILE}${colors.reset}`);
    console.log(`\n${colors.green}Pour corriger automatiquement les problèmes possibles:${colors.reset}`);
    console.log(`${colors.white}npx eslint --ext .js,.jsx,.ts,.tsx src --fix${colors.reset}`);
    
    process.exit(1); // Sortie avec un code d'erreur
  } else {
    console.log(`${colors.green}✓ Aucun problème ESLint détecté! Le code est conforme aux standards.${colors.reset}`);
    
    // Supprimer le rapport s'il n'y a pas de problèmes
    if (fs.existsSync(REPORT_FILE)) {
      fs.unlinkSync(REPORT_FILE);
    }
  }
} catch (error) {
  console.error(`${colors.red}Erreur lors de l'exécution d'ESLint:${colors.reset}`);
  console.error(error.message || error);
  process.exit(1);
} 