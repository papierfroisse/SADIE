/**
 * Script pour la mise à jour sécurisée des dépendances
 * 
 * Ce script analyse les dépendances obsolètes, leur attribue un niveau de risque,
 * et suggère un plan de mise à jour progressif pour minimiser les régressions.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const PACKAGE_JSON_PATH = path.resolve(__dirname, '../package.json');
const REPORTS_DIR = path.resolve(__dirname, '../reports');
const REPORT_FILE = path.join(REPORTS_DIR, 'dependencies-report.json');
const SUMMARY_FILE = path.join(REPORTS_DIR, 'dependencies-summary.md');

// Couleurs pour la console
const COLORS = {
  reset: '\x1b[0m',
  bright: '\x1b[1m',
  green: '\x1b[32m',
  yellow: '\x1b[33m',
  blue: '\x1b[34m',
  magenta: '\x1b[35m',
  cyan: '\x1b[36m',
  red: '\x1b[31m',
};

// Créer le répertoire de rapports s'il n'existe pas
if (!fs.existsSync(REPORTS_DIR)) {
  fs.mkdirSync(REPORTS_DIR, { recursive: true });
}

/**
 * Fonction principale pour analyser et mettre à jour les dépendances
 */
async function updateDependencies() {
  console.log(`${COLORS.bright}${COLORS.blue}Analyse des dépendances du projet...${COLORS.reset}`);
  
  try {
    // 1. Vérifier les mises à jour disponibles
    console.log(`${COLORS.cyan}Recherche des mises à jour disponibles...${COLORS.reset}`);
    const outdatedPackages = getOutdatedPackages();
    
    if (Object.keys(outdatedPackages).length === 0) {
      console.log(`${COLORS.green}Toutes les dépendances sont à jour!${COLORS.reset}`);
      return;
    }
    
    // 2. Analyser les dépendances et attribuer des niveaux de risque
    console.log(`${COLORS.cyan}Analyse des niveaux de risque...${COLORS.reset}`);
    const packageLevels = categorizeDependencies(outdatedPackages);
    
    // 3. Générer un rapport et un plan de mise à jour
    console.log(`${COLORS.cyan}Génération du plan de mise à jour...${COLORS.reset}`);
    const updatePlan = generateUpdatePlan(packageLevels);
    
    // 4. Écrire le rapport dans un fichier JSON
    const report = {
      timestamp: new Date().toISOString(),
      outdatedPackages,
      packageLevels,
      updatePlan,
    };
    
    fs.writeFileSync(REPORT_FILE, JSON.stringify(report, null, 2));
    
    // 5. Générer un rapport au format Markdown
    generateMarkdownReport(report);
    
    // 6. Afficher un résumé dans la console
    printSummary(report);
    
    // 7. Demander à l'utilisateur s'il souhaite procéder à la mise à jour
    await promptForUpdates(updatePlan);
    
  } catch (error) {
    console.error(`${COLORS.red}Erreur lors de l'analyse des dépendances:${COLORS.reset}`, error.message);
    process.exit(1);
  }
}

/**
 * Récupère la liste des packages obsolètes
 */
function getOutdatedPackages() {
  try {
    // Exécuter npm outdated en format JSON
    const outdatedOutput = execSync('npm outdated --json', { 
      cwd: path.resolve(__dirname, '..'),
      stdio: ['ignore', 'pipe', 'ignore'],
    });
    
    return JSON.parse(outdatedOutput.toString() || '{}');
  } catch (error) {
    // npm outdated retourne un code d'erreur s'il trouve des packages obsolètes
    if (error.stdout) {
      try {
        return JSON.parse(error.stdout.toString() || '{}');
      } catch (e) {
        console.error(`${COLORS.red}Erreur lors de l'analyse de la sortie npm outdated:${COLORS.reset}`, e.message);
      }
    }
    return {};
  }
}

/**
 * Catégoriser les dépendances par niveau de risque
 */
function categorizeDependencies(outdatedPackages) {
  const packageJson = require(PACKAGE_JSON_PATH);
  const dependencies = packageJson.dependencies || {};
  const devDependencies = packageJson.devDependencies || {};
  
  const result = {
    critical: [],   // Risque très élevé (React, grandes bibliothèques UI)
    high: [],       // Risque élevé (Redux, bibliothèques d'état, etc.)
    medium: [],     // Risque moyen (utilitaires, formatters, etc.)
    low: [],        // Risque faible (dev dependencies, linters, etc.)
  };
  
  // Liste des packages considérés comme critiques ou à haut risque
  const criticalPackages = ['react', 'react-dom', 'react-router', 'react-router-dom', '@material-ui/core', '@mui/material'];
  const highRiskPackages = ['redux', 'react-redux', '@reduxjs/toolkit', 'mobx', 'mobx-react', 'apollo-client', '@apollo/client'];
  
  // Analyser chaque package obsolète
  Object.entries(outdatedPackages).forEach(([packageName, info]) => {
    const isDev = devDependencies[packageName] !== undefined;
    const currentVersion = info.current;
    const latestVersion = info.latest;
    
    // Extraire les numéros de version majeure
    const currentMajor = parseInt(currentVersion.split('.')[0], 10);
    const latestMajor = parseInt(latestVersion.split('.')[0], 10);
    const hasMajorUpdate = latestMajor > currentMajor;
    
    // Déterminer le niveau de risque
    if (criticalPackages.includes(packageName)) {
      result.critical.push({ packageName, ...info, isDev, hasMajorUpdate });
    } else if (highRiskPackages.includes(packageName)) {
      result.high.push({ packageName, ...info, isDev, hasMajorUpdate });
    } else if (isDev) {
      result.low.push({ packageName, ...info, isDev, hasMajorUpdate });
    } else if (hasMajorUpdate) {
      result.high.push({ packageName, ...info, isDev, hasMajorUpdate });
    } else {
      result.medium.push({ packageName, ...info, isDev, hasMajorUpdate });
    }
  });
  
  return result;
}

/**
 * Générer un plan de mise à jour basé sur les niveaux de risque
 */
function generateUpdatePlan(packageLevels) {
  const plan = [];
  
  // Étape 1: Mettre à jour les dépendances à faible risque
  if (packageLevels.low.length > 0) {
    const packages = packageLevels.low.map(p => p.packageName);
    plan.push({
      phase: 1,
      title: 'Mise à jour des dépendances à faible risque',
      description: 'Mettre à jour les dépendances de développement et les outils',
      command: `npm update ${packages.join(' ')}`,
      packages: packageLevels.low,
    });
  }
  
  // Étape 2: Mettre à jour les dépendances à risque moyen (sans changement majeur)
  const mediumMinorUpdates = packageLevels.medium.filter(p => !p.hasMajorUpdate);
  if (mediumMinorUpdates.length > 0) {
    const packages = mediumMinorUpdates.map(p => p.packageName);
    plan.push({
      phase: 2,
      title: 'Mise à jour des dépendances à risque moyen (pas de changement majeur)',
      description: 'Mettre à jour les utilitaires et bibliothèques secondaires',
      command: `npm update ${packages.join(' ')}`,
      packages: mediumMinorUpdates,
    });
  }
  
  // Étape 3: Mettre à jour les dépendances à risque moyen avec changement majeur
  const mediumMajorUpdates = packageLevels.medium.filter(p => p.hasMajorUpdate);
  if (mediumMajorUpdates.length > 0) {
    mediumMajorUpdates.forEach(pkg => {
      plan.push({
        phase: 3,
        title: `Mise à jour majeure de ${pkg.packageName}`,
        description: `Passage de ${pkg.current} à ${pkg.latest}`,
        command: `npm install ${pkg.packageName}@latest`,
        packages: [pkg],
      });
    });
  }
  
  // Étape 4: Mettre à jour les dépendances à risque élevé sans changement majeur
  const highMinorUpdates = packageLevels.high.filter(p => !p.hasMajorUpdate);
  if (highMinorUpdates.length > 0) {
    const packages = highMinorUpdates.map(p => p.packageName);
    plan.push({
      phase: 4,
      title: 'Mise à jour des dépendances à risque élevé (pas de changement majeur)',
      description: 'Mettre à jour les bibliothèques de gestion d\'état',
      command: `npm update ${packages.join(' ')}`,
      packages: highMinorUpdates,
    });
  }
  
  // Étape 5: Mettre à jour les dépendances à risque élevé avec changement majeur
  const highMajorUpdates = packageLevels.high.filter(p => p.hasMajorUpdate);
  if (highMajorUpdates.length > 0) {
    highMajorUpdates.forEach(pkg => {
      plan.push({
        phase: 5,
        title: `Mise à jour majeure de ${pkg.packageName}`,
        description: `Passage de ${pkg.current} à ${pkg.latest}`,
        command: `npm install ${pkg.packageName}@latest`,
        packages: [pkg],
      });
    });
  }
  
  // Étape 6: Mettre à jour les dépendances critiques sans changement majeur
  const criticalMinorUpdates = packageLevels.critical.filter(p => !p.hasMajorUpdate);
  if (criticalMinorUpdates.length > 0) {
    const packages = criticalMinorUpdates.map(p => p.packageName);
    plan.push({
      phase: 6,
      title: 'Mise à jour des dépendances critiques (pas de changement majeur)',
      description: 'Mettre à jour React et les bibliothèques UI principales',
      command: `npm update ${packages.join(' ')}`,
      packages: criticalMinorUpdates,
    });
  }
  
  // Étape 7: Mettre à jour les dépendances critiques avec changement majeur
  const criticalMajorUpdates = packageLevels.critical.filter(p => p.hasMajorUpdate);
  if (criticalMajorUpdates.length > 0) {
    criticalMajorUpdates.forEach(pkg => {
      plan.push({
        phase: 7,
        title: `Mise à jour majeure de ${pkg.packageName}`,
        description: `Passage de ${pkg.current} à ${pkg.latest}`,
        command: `npm install ${pkg.packageName}@latest`,
        packages: [pkg],
        manualSteps: [
          'Lire les notes de version pour comprendre les changements majeurs',
          'Mettre à jour le code en suivant les guides de migration officiels',
          'Exécuter les tests unitaires et d\'intégration',
          'Vérifier les fonctionnalités critiques manuellement'
        ]
      });
    });
  }
  
  return plan;
}

/**
 * Générer un rapport au format Markdown
 */
function generateMarkdownReport(report) {
  const { outdatedPackages, packageLevels, updatePlan } = report;
  
  const markdown = `# Rapport de dépendances - SADIE
  
## Généré le ${new Date().toLocaleDateString('fr-FR')} à ${new Date().toLocaleTimeString('fr-FR')}

## Résumé

- **Dépendances obsolètes**: ${Object.keys(outdatedPackages).length}
- **Dépendances critiques à mettre à jour**: ${packageLevels.critical.length}
- **Dépendances à risque élevé**: ${packageLevels.high.length}
- **Dépendances à risque moyen**: ${packageLevels.medium.length}
- **Dépendances à faible risque**: ${packageLevels.low.length}

## Dépendances obsolètes par niveau de risque

### Niveau Critique

${packageLevels.critical.length === 0 ? '_Aucune dépendance critique à mettre à jour_' : 
packageLevels.critical.map(pkg => `- **${pkg.packageName}**: ${pkg.current} -> ${pkg.latest} ${pkg.hasMajorUpdate ? '(Mise à jour majeure ⚠️)' : ''}`).join('\n')}

### Risque Élevé

${packageLevels.high.length === 0 ? '_Aucune dépendance à risque élevé_' : 
packageLevels.high.map(pkg => `- **${pkg.packageName}**: ${pkg.current} -> ${pkg.latest} ${pkg.hasMajorUpdate ? '(Mise à jour majeure ⚠️)' : ''}`).join('\n')}

### Risque Moyen

${packageLevels.medium.length === 0 ? '_Aucune dépendance à risque moyen_' : 
packageLevels.medium.map(pkg => `- **${pkg.packageName}**: ${pkg.current} -> ${pkg.latest} ${pkg.hasMajorUpdate ? '(Mise à jour majeure ⚠️)' : ''}`).join('\n')}

### Risque Faible

${packageLevels.low.length === 0 ? '_Aucune dépendance à faible risque_' : 
packageLevels.low.map(pkg => `- **${pkg.packageName}**: ${pkg.current} -> ${pkg.latest} ${pkg.hasMajorUpdate ? '(Mise à jour majeure)' : ''}`).join('\n')}

## Plan de mise à jour recommandé

${updatePlan.map(phase => `
### Phase ${phase.phase}: ${phase.title}

${phase.description}

\`\`\`bash
${phase.command}
\`\`\`

${phase.manualSteps ? 
  `**Étapes manuelles supplémentaires:**\n\n${phase.manualSteps.map(step => `- ${step}`).join('\n')}` : ''}
`).join('\n')}

## Recommandations générales

1. **Faire des sauvegardes**: Toujours sauvegarder l'état actuel du projet avant de mettre à jour les dépendances
2. **Mise à jour progressive**: Suivre le plan par phases et vérifier après chaque phase que tout fonctionne
3. **Tests**: Exécuter les tests après chaque mise à jour pour détecter rapidement les problèmes
4. **Versionnement**: Utilisez Git pour pouvoir revenir en arrière si nécessaire

## Dépendances avec des vulnérabilités connues

${runSecurityAudit()}

---

*Ce rapport a été généré automatiquement par le script update-dependencies.js*
`;

  fs.writeFileSync(SUMMARY_FILE, markdown);
}

/**
 * Exécuter un audit de sécurité
 */
function runSecurityAudit() {
  try {
    // Exécuter npm audit
    const auditOutput = execSync('npm audit --json', { 
      cwd: path.resolve(__dirname, '..'),
      stdio: ['ignore', 'pipe', 'ignore'],
    });
    
    const auditResult = JSON.parse(auditOutput.toString() || '{"vulnerabilities":{}}');
    const vulnerabilities = auditResult.vulnerabilities || {};
    const vulnEntries = Object.entries(vulnerabilities);
    
    if (vulnEntries.length === 0) {
      return '_Aucune vulnérabilité détectée_';
    }
    
    // Formater les vulnérabilités pour le rapport
    return vulnEntries.map(([pkg, info]) => {
      const severity = info.severity || 'unknown';
      const via = Array.isArray(info.via) ? info.via.filter(v => typeof v === 'string').join(', ') : (info.via || 'unknown');
      const fixAvailable = info.fixAvailable ? 'Oui' : 'Non';
      
      return `- **${pkg}**: Sévérité: ${severity}, Via: ${via}, Correctif disponible: ${fixAvailable}`;
    }).join('\n');
    
  } catch (error) {
    if (error.stdout) {
      try {
        const auditResult = JSON.parse(error.stdout.toString() || '{"vulnerabilities":{}}');
        const vulnerabilities = auditResult.vulnerabilities || {};
        const vulnEntries = Object.entries(vulnerabilities);
        
        if (vulnEntries.length === 0) {
          return '_Aucune vulnérabilité détectée_';
        }
        
        return vulnEntries.map(([pkg, info]) => {
          const severity = info.severity || 'unknown';
          const via = Array.isArray(info.via) ? info.via.filter(v => typeof v === 'string').join(', ') : (info.via || 'unknown');
          const fixAvailable = info.fixAvailable ? 'Oui' : 'Non';
          
          return `- **${pkg}**: Sévérité: ${severity}, Via: ${via}, Correctif disponible: ${fixAvailable}`;
        }).join('\n');
      } catch (e) {
        return '_Erreur lors de l\'analyse des vulnérabilités_';
      }
    }
    return '_Erreur lors de l\'audit de sécurité_';
  }
}

/**
 * Afficher un résumé des mises à jour disponibles
 */
function printSummary(report) {
  const { outdatedPackages, packageLevels, updatePlan } = report;
  
  console.log('\n');
  console.log(`${COLORS.bright}${COLORS.green}=== Rapport de dépendances ====${COLORS.reset}`);
  console.log(`${COLORS.bright}Dépendances obsolètes:${COLORS.reset} ${Object.keys(outdatedPackages).length}`);
  
  // Afficher par niveau de risque
  console.log(`${COLORS.bright}${COLORS.red}Dépendances critiques:${COLORS.reset} ${packageLevels.critical.length}`);
  console.log(`${COLORS.bright}${COLORS.yellow}Dépendances à risque élevé:${COLORS.reset} ${packageLevels.high.length}`);
  console.log(`${COLORS.bright}${COLORS.cyan}Dépendances à risque moyen:${COLORS.reset} ${packageLevels.medium.length}`);
  console.log(`${COLORS.bright}${COLORS.green}Dépendances à faible risque:${COLORS.reset} ${packageLevels.low.length}`);
  
  console.log('\n');
  console.log(`${COLORS.bright}${COLORS.magenta}Plan de mise à jour recommandé:${COLORS.reset}`);
  updatePlan.forEach(phase => {
    console.log(`  ${COLORS.cyan}Phase ${phase.phase}: ${phase.title}${COLORS.reset}`);
  });
  
  console.log('\n');
  console.log(`${COLORS.bright}${COLORS.blue}Rapport détaillé généré dans:${COLORS.reset}`);
  console.log(`  ${COLORS.bright}${SUMMARY_FILE}${COLORS.reset}`);
  console.log(`  ${COLORS.bright}${REPORT_FILE}${COLORS.reset}`);
  console.log('\n');
}

/**
 * Demander à l'utilisateur s'il souhaite procéder aux mises à jour
 */
async function promptForUpdates(updatePlan) {
  if (updatePlan.length === 0) {
    return;
  }
  
  console.log(`${COLORS.yellow}Souhaitez-vous procéder aux mises à jour maintenant?${COLORS.reset}`);
  console.log(`${COLORS.bright}(Les phases seront exécutées une par une et vous pourrez annuler à tout moment)${COLORS.reset}`);
  
  const readline = require('readline').createInterface({
    input: process.stdin,
    output: process.stdout
  });
  
  // Fonction pour poser une question et obtenir une réponse
  const askQuestion = (question) => {
    return new Promise((resolve) => {
      readline.question(question, (answer) => {
        resolve(answer.toLowerCase());
      });
    });
  };
  
  const answer = await askQuestion(`${COLORS.yellow}Procéder aux mises à jour? (o/n)${COLORS.reset} `);
  
  if (answer === 'o' || answer === 'oui' || answer === 'y' || answer === 'yes') {
    // Exécuter les phases une par une
    for (const phase of updatePlan) {
      console.log(`\n${COLORS.bright}${COLORS.blue}=== Phase ${phase.phase}: ${phase.title} ====${COLORS.reset}`);
      console.log(`${COLORS.cyan}${phase.description}${COLORS.reset}`);
      console.log(`${COLORS.bright}Commande:${COLORS.reset} ${phase.command}`);
      
      const confirmPhase = await askQuestion(`${COLORS.yellow}Exécuter cette phase? (o/n/q pour quitter)${COLORS.reset} `);
      
      if (confirmPhase === 'q' || confirmPhase === 'quitter' || confirmPhase === 'quit') {
        console.log(`${COLORS.yellow}Mise à jour annulée.${COLORS.reset}`);
        break;
      }
      
      if (confirmPhase === 'o' || confirmPhase === 'oui' || confirmPhase === 'y' || confirmPhase === 'yes') {
        try {
          console.log(`${COLORS.cyan}Exécution de la commande...${COLORS.reset}`);
          execSync(phase.command, { 
            cwd: path.resolve(__dirname, '..'),
            stdio: 'inherit'
          });
          
          console.log(`${COLORS.green}✓ Phase ${phase.phase} terminée avec succès!${COLORS.reset}`);
          
          // Vérifier si des étapes manuelles sont nécessaires
          if (phase.manualSteps && phase.manualSteps.length > 0) {
            console.log(`\n${COLORS.bright}${COLORS.yellow}Étapes manuelles nécessaires:${COLORS.reset}`);
            phase.manualSteps.forEach((step, index) => {
              console.log(`  ${COLORS.yellow}${index + 1}. ${step}${COLORS.reset}`);
            });
            
            await askQuestion(`\n${COLORS.yellow}Appuyez sur Entrée après avoir effectué ces étapes...${COLORS.reset}`);
          }
          
          // Exécuter les tests après chaque phase
          const runTests = await askQuestion(`${COLORS.yellow}Exécuter les tests? (o/n)${COLORS.reset} `);
          
          if (runTests === 'o' || runTests === 'oui' || runTests === 'y' || runTests === 'yes') {
            try {
              console.log(`${COLORS.cyan}Exécution des tests...${COLORS.reset}`);
              execSync('npm run test:ci', { 
                cwd: path.resolve(__dirname, '..'),
                stdio: 'inherit'
              });
              console.log(`${COLORS.green}✓ Tests réussis!${COLORS.reset}`);
            } catch (error) {
              console.error(`${COLORS.red}✗ Les tests ont échoué:${COLORS.reset}`, error.message);
              const continueAnyway = await askQuestion(`${COLORS.red}Continuer malgré l'échec des tests? (o/n)${COLORS.reset} `);
              if (continueAnyway !== 'o' && continueAnyway !== 'oui' && continueAnyway !== 'y' && continueAnyway !== 'yes') {
                console.log(`${COLORS.yellow}Mise à jour annulée.${COLORS.reset}`);
                break;
              }
            }
          }
          
        } catch (error) {
          console.error(`${COLORS.red}✗ Erreur lors de l'exécution de la phase ${phase.phase}:${COLORS.reset}`, error.message);
          const continueAnyway = await askQuestion(`${COLORS.red}Continuer malgré l'erreur? (o/n)${COLORS.reset} `);
          if (continueAnyway !== 'o' && continueAnyway !== 'oui' && continueAnyway !== 'y' && continueAnyway !== 'yes') {
            console.log(`${COLORS.yellow}Mise à jour annulée.${COLORS.reset}`);
            break;
          }
        }
      } else {
        console.log(`${COLORS.yellow}Phase ${phase.phase} ignorée.${COLORS.reset}`);
      }
    }
    
    console.log(`\n${COLORS.bright}${COLORS.green}Processus de mise à jour terminé!${COLORS.reset}`);
  } else {
    console.log(`${COLORS.yellow}Mise à jour annulée. Vous pouvez consulter le plan de mise à jour recommandé dans le rapport.${COLORS.reset}`);
  }
  
  readline.close();
}

// Exécuter le script
updateDependencies().catch(err => {
  console.error(`${COLORS.red}Erreur:${COLORS.reset}`, err);
  process.exit(1);
}); 