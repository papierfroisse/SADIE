/**
 * Script de validation globale du code
 * 
 * Ce script exécute toutes les validations disponibles (TypeScript, ESLint, Prettier, Tests)
 * et génère un rapport de synthèse des problèmes détectés.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const REPORTS_DIR = path.resolve(__dirname, '../reports');
const SUMMARY_FILE = path.join(REPORTS_DIR, 'validation-summary.json');
const SUMMARY_MD_FILE = path.join(REPORTS_DIR, 'validation-summary.md');

// Créer le répertoire de rapports s'il n'existe pas
if (!fs.existsSync(REPORTS_DIR)) {
  fs.mkdirSync(REPORTS_DIR, { recursive: true });
}

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

/**
 * Fonction principale qui exécute toutes les validations
 */
async function validateAll() {
  console.log(`${COLORS.bright}${COLORS.blue}Exécution de toutes les validations...${COLORS.reset}`);
  
  const startTime = Date.now();
  const results = {
    timestamp: new Date().toISOString(),
    summary: {
      typescript: { success: false, errors: 0, warnings: 0 },
      eslint: { success: false, errors: 0, warnings: 0 },
      prettier: { success: false, errors: 0 },
      tests: { success: false, passed: 0, failed: 0 },
    },
    details: {
      typescript: null,
      eslint: null,
      prettier: null,
      tests: null,
    }
  };
  
  // 1. Validation TypeScript
  console.log(`${COLORS.cyan}Exécution de la validation TypeScript...${COLORS.reset}`);
  results.details.typescript = await runTypescriptValidation();
  results.summary.typescript = {
    success: results.details.typescript.success,
    errors: results.details.typescript.errors.length,
    warnings: 0,
  };
  
  // 2. Validation ESLint
  console.log(`${COLORS.cyan}Exécution de la validation ESLint...${COLORS.reset}`);
  results.details.eslint = await runEslintValidation();
  results.summary.eslint = {
    success: results.details.eslint.success,
    errors: results.details.eslint.errorCount,
    warnings: results.details.eslint.warningCount,
  };
  
  // 3. Validation Prettier
  console.log(`${COLORS.cyan}Exécution de la validation Prettier...${COLORS.reset}`);
  results.details.prettier = await runPrettierValidation();
  results.summary.prettier = {
    success: results.details.prettier.success,
    errors: results.details.prettier.files.length,
  };
  
  // 4. Exécution des tests unitaires
  console.log(`${COLORS.cyan}Exécution des tests unitaires...${COLORS.reset}`);
  results.details.tests = await runUnitTests();
  results.summary.tests = {
    success: results.details.tests.success,
    passed: results.details.tests.numPassedTests,
    failed: results.details.tests.numFailedTests,
  };
  
  // Calculer le temps total
  const endTime = Date.now();
  results.executionTime = endTime - startTime;
  
  // Vérifier le succès global
  const globalSuccess = 
    results.summary.typescript.success && 
    results.summary.eslint.success && 
    results.summary.prettier.success &&
    results.summary.tests.success;
  
  // Générer un résumé
  results.globalSuccess = globalSuccess;
  results.totalErrors = 
    results.summary.typescript.errors + 
    results.summary.eslint.errors + 
    results.summary.prettier.errors +
    results.summary.tests.failed;
  
  results.totalWarnings = results.summary.eslint.warnings;
  
  // Écrire le rapport
  fs.writeFileSync(SUMMARY_FILE, JSON.stringify(results, null, 2));
  
  // Générer un rapport markdown
  generateMarkdownReport(results);
  
  // Afficher un résumé
  printSummary(results);
  
  return results;
}

/**
 * Exécute la validation TypeScript
 */
async function runTypescriptValidation() {
  try {
    // Utiliser notre script de validation TypeScript
    execSync('node scripts/validate-types.js', { 
      cwd: path.resolve(__dirname, '..'),
      stdio: 'ignore',
    });
    
    // Lire le rapport JSON généré
    const reportPath = path.join(REPORTS_DIR, 'typescript-report.json');
    
    if (fs.existsSync(reportPath)) {
      const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
      return {
        success: report.totalErrors === 0,
        errors: report.errors || [],
        errorsByFile: report.errorsByFile || {},
      };
    }
    
    // Si aucun rapport n'est trouvé mais que la commande a réussi, considérer comme un succès
    return { success: true, errors: [], errorsByFile: {} };
    
  } catch (error) {
    // Erreur pendant l'exécution du script de validation
    return { 
      success: false, 
      errors: [{ 
        message: `Erreur lors de la validation TypeScript: ${error.message}`,
        location: { file: 'unknown', line: 0, column: 0 }
      }],
      errorsByFile: {}
    };
  }
}

/**
 * Exécute la validation ESLint
 */
async function runEslintValidation() {
  try {
    // Exécuter ESLint avec sortie JSON
    execSync('npm run lint:report', { 
      cwd: path.resolve(__dirname, '..'),
      stdio: 'ignore',
    });
    
    // Lire le rapport JSON
    const reportPath = path.join(REPORTS_DIR, 'eslint-report.json');
    
    if (fs.existsSync(reportPath)) {
      const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
      
      // Calculer le nombre total d'erreurs et d'avertissements
      let errorCount = 0;
      let warningCount = 0;
      
      report.forEach(result => {
        errorCount += result.errorCount || 0;
        warningCount += result.warningCount || 0;
      });
      
      return {
        success: errorCount === 0,
        errorCount,
        warningCount,
        results: report,
      };
    }
    
    // Si aucun rapport n'est trouvé mais que la commande a réussi, considérer comme un succès
    return { success: true, errorCount: 0, warningCount: 0, results: [] };
    
  } catch (error) {
    // Essayer de récupérer le rapport même si la commande a échoué
    try {
      const reportPath = path.join(REPORTS_DIR, 'eslint-report.json');
      
      if (fs.existsSync(reportPath)) {
        const report = JSON.parse(fs.readFileSync(reportPath, 'utf8'));
        
        let errorCount = 0;
        let warningCount = 0;
        
        report.forEach(result => {
          errorCount += result.errorCount || 0;
          warningCount += result.warningCount || 0;
        });
        
        return {
          success: errorCount === 0,
          errorCount,
          warningCount,
          results: report,
        };
      }
    } catch (e) {
      // Ignorer l'erreur et utiliser le résultat par défaut
    }
    
    // Si tout échoue, retourner une erreur
    return { 
      success: false, 
      errorCount: 1, 
      warningCount: 0, 
      results: [{ 
        filePath: 'unknown',
        messages: [{ 
          severity: 2, 
          message: `Erreur lors de la validation ESLint: ${error.message}` 
        }]
      }]
    };
  }
}

/**
 * Exécute la validation Prettier
 */
async function runPrettierValidation() {
  try {
    // Exécuter Prettier avec rapport
    execSync('npm run format:report', { 
      cwd: path.resolve(__dirname, '..'),
      stdio: 'ignore',
    });
    
    // Lire le rapport
    const reportPath = path.join(REPORTS_DIR, 'prettier-report.txt');
    
    if (fs.existsSync(reportPath)) {
      const report = fs.readFileSync(reportPath, 'utf8');
      
      // Parser le rapport pour trouver les fichiers avec des problèmes
      const fileRegex = /.*\.(?:js|jsx|ts|tsx|json|css|scss|md)$/gm;
      const files = report.match(fileRegex) || [];
      
      return {
        success: files.length === 0,
        files: files,
        report: report,
      };
    }
    
    // Si aucun rapport n'est trouvé mais que la commande a réussi, considérer comme un succès
    return { success: true, files: [], report: '' };
    
  } catch (error) {
    // Si Prettier a trouvé des problèmes, essayer quand même de lire le rapport
    try {
      const reportPath = path.join(REPORTS_DIR, 'prettier-report.txt');
      
      if (fs.existsSync(reportPath)) {
        const report = fs.readFileSync(reportPath, 'utf8');
        
        // Parser le rapport pour trouver les fichiers avec des problèmes
        const fileRegex = /.*\.(?:js|jsx|ts|tsx|json|css|scss|md)$/gm;
        const files = report.match(fileRegex) || [];
        
        return {
          success: files.length === 0,
          files: files,
          report: report,
        };
      }
    } catch (e) {
      // Ignorer l'erreur et utiliser le résultat par défaut
    }
    
    // Si tout échoue, retourner une erreur
    return { 
      success: false, 
      files: ['unknown'], 
      report: `Erreur lors de la validation Prettier: ${error.message}` 
    };
  }
}

/**
 * Exécute les tests unitaires
 */
async function runUnitTests() {
  try {
    // Exécuter les tests avec Jest
    execSync('npm run test:ci', { 
      cwd: path.resolve(__dirname, '..'),
      stdio: 'ignore',
    });
    
    // Si les tests passent, considérer comme un succès
    return { 
      success: true, 
      numPassedTests: 1, // Valeur par défaut, nous ne pouvons pas connaître le nombre exact sans parser la sortie
      numFailedTests: 0,
      testResults: []
    };
    
  } catch (error) {
    // Les tests ont échoué
    return { 
      success: false, 
      numPassedTests: 0,
      numFailedTests: 1, // Valeur par défaut
      testResults: [{
        name: 'unknown',
        status: 'failed',
        message: `Erreur lors de l'exécution des tests: ${error.message}`
      }]
    };
  }
}

/**
 * Génère un rapport Markdown
 */
function generateMarkdownReport(results) {
  const { summary, details, globalSuccess, totalErrors, totalWarnings, executionTime } = results;
  
  const markdown = `# Rapport de validation du code - SADIE

## Généré le ${new Date().toLocaleDateString('fr-FR')} à ${new Date().toLocaleTimeString('fr-FR')}

## Résumé

- **Statut global**: ${globalSuccess ? '✅ Succès' : '❌ Échec'}
- **Erreurs totales**: ${totalErrors}
- **Avertissements**: ${totalWarnings}
- **Temps d'exécution**: ${(executionTime / 1000).toFixed(2)} secondes

## Validation TypeScript

- **Statut**: ${summary.typescript.success ? '✅ Succès' : '❌ Échec'}
- **Erreurs**: ${summary.typescript.errors}

${summary.typescript.errors > 0 ? formatTypescriptErrors(details.typescript) : ''}

## Validation ESLint

- **Statut**: ${summary.eslint.success ? '✅ Succès' : '❌ Échec'}
- **Erreurs**: ${summary.eslint.errors}
- **Avertissements**: ${summary.eslint.warnings}

${summary.eslint.errors + summary.eslint.warnings > 0 ? formatEslintErrors(details.eslint) : ''}

## Validation Prettier

- **Statut**: ${summary.prettier.success ? '✅ Succès' : '❌ Échec'}
- **Fichiers mal formatés**: ${summary.prettier.errors}

${summary.prettier.errors > 0 ? formatPrettierErrors(details.prettier) : ''}

## Tests unitaires

- **Statut**: ${summary.tests.success ? '✅ Succès' : '❌ Échec'}
- **Tests réussis**: ${summary.tests.passed}
- **Tests échoués**: ${summary.tests.failed}

${summary.tests.failed > 0 ? formatTestErrors(details.tests) : ''}

## Comment résoudre les problèmes

### TypeScript

Pour corriger les erreurs TypeScript:
\`\`\`bash
npm run type-check
\`\`\`

### ESLint

Pour corriger automatiquement les problèmes ESLint:
\`\`\`bash
npm run lint:fix
\`\`\`

### Prettier

Pour formater automatiquement les fichiers:
\`\`\`bash
npm run format:fix
\`\`\`

### Tout corriger à la fois

Pour tenter de corriger tous les problèmes automatiquement:
\`\`\`bash
npm run fix-all
\`\`\`

---

*Ce rapport a été généré automatiquement par le script validate-all.js*
`;

  fs.writeFileSync(SUMMARY_MD_FILE, markdown);
}

/**
 * Formater les erreurs TypeScript pour le rapport Markdown
 */
function formatTypescriptErrors(tsResults) {
  if (!tsResults || !tsResults.errorsByFile || Object.keys(tsResults.errorsByFile).length === 0) {
    return '_Détails des erreurs non disponibles_';
  }
  
  let output = '### Erreurs TypeScript par fichier\n\n';
  
  Object.entries(tsResults.errorsByFile).forEach(([file, errors]) => {
    output += `#### ${file}\n\n`;
    
    errors.slice(0, 5).forEach(error => {
      output += `- **Ligne ${error.location.line}**: ${error.message}\n`;
    });
    
    if (errors.length > 5) {
      output += `- _... et ${errors.length - 5} autres erreurs_\n`;
    }
    
    output += '\n';
  });
  
  return output;
}

/**
 * Formater les erreurs ESLint pour le rapport Markdown
 */
function formatEslintErrors(eslintResults) {
  if (!eslintResults || !eslintResults.results || eslintResults.results.length === 0) {
    return '_Détails des erreurs non disponibles_';
  }
  
  let output = '### Problèmes ESLint par fichier\n\n';
  
  // Filtrer les fichiers avec des problèmes
  const filesWithIssues = eslintResults.results.filter(
    result => (result.errorCount + result.warningCount) > 0
  );
  
  // Limiter à 10 fichiers pour garder le rapport concis
  filesWithIssues.slice(0, 10).forEach(result => {
    const relativePath = path.relative(path.resolve(__dirname, '..'), result.filePath);
    output += `#### ${relativePath}\n\n`;
    
    // Limiter à 5 messages par fichier
    result.messages.slice(0, 5).forEach(msg => {
      const type = msg.severity === 2 ? '🔴 Erreur' : '🟡 Avertissement';
      output += `- **${type} (ligne ${msg.line})**: ${msg.message} (${msg.ruleId})\n`;
    });
    
    if (result.messages.length > 5) {
      output += `- _... et ${result.messages.length - 5} autres problèmes_\n`;
    }
    
    output += '\n';
  });
  
  if (filesWithIssues.length > 10) {
    output += `_... et des problèmes dans ${filesWithIssues.length - 10} autres fichiers_\n\n`;
  }
  
  return output;
}

/**
 * Formater les erreurs Prettier pour le rapport Markdown
 */
function formatPrettierErrors(prettierResults) {
  if (!prettierResults || !prettierResults.files || prettierResults.files.length === 0) {
    return '_Détails des erreurs non disponibles_';
  }
  
  let output = '### Fichiers mal formatés\n\n';
  
  // Limiter à 15 fichiers pour garder le rapport concis
  prettierResults.files.slice(0, 15).forEach(file => {
    output += `- ${file}\n`;
  });
  
  if (prettierResults.files.length > 15) {
    output += `- _... et ${prettierResults.files.length - 15} autres fichiers_\n`;
  }
  
  return output;
}

/**
 * Formater les erreurs de test pour le rapport Markdown
 */
function formatTestErrors(testResults) {
  if (!testResults || !testResults.testResults || testResults.testResults.length === 0) {
    return '_Détails des tests échoués non disponibles_';
  }
  
  let output = '### Tests échoués\n\n';
  
  testResults.testResults.forEach(test => {
    if (test.status === 'failed') {
      output += `- **${test.name}**: ${test.message}\n`;
    }
  });
  
  return output;
}

/**
 * Afficher un résumé dans la console
 */
function printSummary(results) {
  const { summary, globalSuccess, totalErrors, totalWarnings, executionTime } = results;
  
  console.log('\n');
  console.log(`${COLORS.bright}${COLORS.blue}=== Résumé de la validation ===${COLORS.reset}`);
  
  // Statut global
  if (globalSuccess) {
    console.log(`${COLORS.bright}${COLORS.green}✓ Statut global: Succès${COLORS.reset}`);
  } else {
    console.log(`${COLORS.bright}${COLORS.red}✗ Statut global: Échec${COLORS.reset}`);
  }
  
  console.log(`${COLORS.bright}Erreurs totales:${COLORS.reset} ${totalErrors}`);
  console.log(`${COLORS.bright}Avertissements:${COLORS.reset} ${totalWarnings}`);
  console.log(`${COLORS.bright}Temps d'exécution:${COLORS.reset} ${(executionTime / 1000).toFixed(2)} secondes`);
  
  console.log('\n');
  
  // TypeScript
  if (summary.typescript.success) {
    console.log(`${COLORS.green}✓ TypeScript: Pas d'erreur${COLORS.reset}`);
  } else {
    console.log(`${COLORS.red}✗ TypeScript: ${summary.typescript.errors} erreur(s)${COLORS.reset}`);
  }
  
  // ESLint
  if (summary.eslint.success) {
    console.log(`${COLORS.green}✓ ESLint: Pas d'erreur${COLORS.reset}`);
  } else {
    console.log(`${COLORS.red}✗ ESLint: ${summary.eslint.errors} erreur(s)${COLORS.reset}`);
  }
  if (summary.eslint.warnings > 0) {
    console.log(`${COLORS.yellow}⚠ ESLint: ${summary.eslint.warnings} avertissement(s)${COLORS.reset}`);
  }
  
  // Prettier
  if (summary.prettier.success) {
    console.log(`${COLORS.green}✓ Prettier: Tous les fichiers sont bien formatés${COLORS.reset}`);
  } else {
    console.log(`${COLORS.red}✗ Prettier: ${summary.prettier.errors} fichier(s) mal formaté(s)${COLORS.reset}`);
  }
  
  // Tests
  if (summary.tests.success) {
    console.log(`${COLORS.green}✓ Tests: Tous les tests ont réussi${COLORS.reset}`);
  } else {
    console.log(`${COLORS.red}✗ Tests: ${summary.tests.failed} test(s) échoué(s)${COLORS.reset}`);
  }
  
  console.log('\n');
  console.log(`${COLORS.bright}${COLORS.magenta}Rapport détaillé généré dans:${COLORS.reset}`);
  console.log(`  ${COLORS.bright}${SUMMARY_MD_FILE}${COLORS.reset}`);
  console.log(`  ${COLORS.bright}${SUMMARY_FILE}${COLORS.reset}`);
  
  if (!globalSuccess) {
    console.log('\n');
    console.log(`${COLORS.bright}${COLORS.yellow}Pour corriger automatiquement certains problèmes:${COLORS.reset}`);
    console.log(`  ${COLORS.bright}npm run fix-all${COLORS.reset}`);
    console.log(`  ${COLORS.bright}npm run lint:fix${COLORS.reset} (pour ESLint uniquement)`);
    console.log(`  ${COLORS.bright}npm run format:fix${COLORS.reset} (pour Prettier uniquement)`);
  }
  
  console.log('\n');
}

// Exécuter toutes les validations
validateAll().then(results => {
  // Sortir avec un code d'erreur si des problèmes ont été détectés
  if (!results.globalSuccess) {
    process.exit(1);
  }
}).catch(err => {
  console.error(`${COLORS.red}Erreur lors de l'exécution des validations:${COLORS.reset}`, err);
  process.exit(1);
}); 