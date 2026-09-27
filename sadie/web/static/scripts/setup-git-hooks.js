/**
 * Script pour configurer les hooks Git pre-commit
 * 
 * Ce script installe husky et configurer des hooks Git pour exécuter
 * automatiquement les validations de code avant chaque commit.
 */

const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Configuration
const HOOKS_DIR = path.resolve(__dirname, '../.husky');
const PRE_COMMIT_HOOK = path.join(HOOKS_DIR, 'pre-commit');

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
 * Fonction principale pour configurer les hooks Git
 */
async function setupGitHooks() {
  console.log(`${COLORS.bright}${COLORS.blue}Configuration des hooks Git pre-commit...${COLORS.reset}`);
  
  try {
    // 1. Vérifier si husky est installé
    if (!isHuskyInstalled()) {
      console.log(`${COLORS.yellow}Husky n'est pas installé. Installation en cours...${COLORS.reset}`);
      installHusky();
    }
    
    // 2. Créer le répertoire des hooks (si nécessaire)
    if (!fs.existsSync(HOOKS_DIR)) {
      console.log(`${COLORS.yellow}Création du répertoire .husky...${COLORS.reset}`);
      fs.mkdirSync(HOOKS_DIR, { recursive: true });
    }
    
    // 3. Créer ou mettre à jour le hook pre-commit
    console.log(`${COLORS.cyan}Mise à jour du hook pre-commit...${COLORS.reset}`);
    createPreCommitHook();
    
    // 4. Vérifier si lint-staged est installé, sinon l'installer
    if (!isLintStagedInstalled()) {
      console.log(`${COLORS.yellow}lint-staged n'est pas installé. Installation en cours...${COLORS.reset}`);
      installLintStaged();
    }
    
    // 5. Créer la configuration de lint-staged
    console.log(`${COLORS.cyan}Mise à jour de la configuration lint-staged...${COLORS.reset}`);
    createLintStagedConfig();
    
    console.log(`${COLORS.bright}${COLORS.green}Les hooks Git ont été configurés avec succès!${COLORS.reset}`);
    
    // Afficher un résumé des hooks configurés
    printSummary();
    
  } catch (error) {
    console.error(`${COLORS.red}Erreur lors de la configuration des hooks Git:${COLORS.reset}`, error.message);
    process.exit(1);
  }
}

/**
 * Vérifie si husky est installé
 */
function isHuskyInstalled() {
  try {
    const packageJson = require('../package.json');
    return packageJson.devDependencies && packageJson.devDependencies.husky;
  } catch (error) {
    return false;
  }
}

/**
 * Installe husky
 */
function installHusky() {
  try {
    execSync('npm install husky --save-dev', { 
      cwd: path.resolve(__dirname, '..'),
      stdio: 'inherit'
    });
    
    // Initialiser husky
    execSync('npx husky install', { 
      cwd: path.resolve(__dirname, '..'),
      stdio: 'inherit'
    });
    
    // Ajouter le script de préparation husky dans package.json
    updatePackageJson();
    
    console.log(`${COLORS.green}Husky a été installé avec succès!${COLORS.reset}`);
  } catch (error) {
    console.error(`${COLORS.red}Erreur lors de l'installation de husky:${COLORS.reset}`, error.message);
    throw error;
  }
}

/**
 * Met à jour package.json pour ajouter le script prepare
 */
function updatePackageJson() {
  try {
    const packageJsonPath = path.resolve(__dirname, '../package.json');
    const packageJson = require(packageJsonPath);
    
    // Ajouter le script prepare s'il n'existe pas
    if (!packageJson.scripts) {
      packageJson.scripts = {};
    }
    
    packageJson.scripts.prepare = 'husky install';
    
    // Écrire les changements dans package.json
    fs.writeFileSync(packageJsonPath, JSON.stringify(packageJson, null, 2));
    
    console.log(`${COLORS.green}Script prepare ajouté à package.json${COLORS.reset}`);
  } catch (error) {
    console.error(`${COLORS.red}Erreur lors de la mise à jour de package.json:${COLORS.reset}`, error.message);
    throw error;
  }
}

/**
 * Crée le hook pre-commit
 */
function createPreCommitHook() {
  const preCommitContent = `#!/usr/bin/env sh
. "$(dirname -- "$0")/_/husky.sh"

echo "${COLORS.cyan}Exécution des vérifications pre-commit...${COLORS.reset}"
npx lint-staged
`;

  // Écrire le hook pre-commit
  fs.writeFileSync(PRE_COMMIT_HOOK, preCommitContent);
  
  // Rendre le hook exécutable
  fs.chmodSync(PRE_COMMIT_HOOK, '755');
  
  console.log(`${COLORS.green}Hook pre-commit créé avec succès!${COLORS.reset}`);
}

/**
 * Vérifie si lint-staged est installé
 */
function isLintStagedInstalled() {
  try {
    const packageJson = require('../package.json');
    return packageJson.devDependencies && packageJson.devDependencies['lint-staged'];
  } catch (error) {
    return false;
  }
}

/**
 * Installe lint-staged
 */
function installLintStaged() {
  try {
    execSync('npm install lint-staged --save-dev', { 
      cwd: path.resolve(__dirname, '..'),
      stdio: 'inherit'
    });
    
    console.log(`${COLORS.green}lint-staged a été installé avec succès!${COLORS.reset}`);
  } catch (error) {
    console.error(`${COLORS.red}Erreur lors de l'installation de lint-staged:${COLORS.reset}`, error.message);
    throw error;
  }
}

/**
 * Crée la configuration de lint-staged
 */
function createLintStagedConfig() {
  const lintStagedConfigPath = path.resolve(__dirname, '../.lintstagedrc');
  const lintStagedConfig = {
    "src/**/*.{ts,tsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "src/**/*.{js,jsx}": [
      "eslint --fix",
      "prettier --write"
    ],
    "src/**/*.{css,scss}": [
      "prettier --write"
    ],
    "src/**/*.{json,md}": [
      "prettier --write"
    ]
  };
  
  // Écrire la configuration de lint-staged
  fs.writeFileSync(lintStagedConfigPath, JSON.stringify(lintStagedConfig, null, 2));
  
  console.log(`${COLORS.green}Configuration lint-staged créée avec succès!${COLORS.reset}`);
}

/**
 * Affiche un résumé des hooks configurés
 */
function printSummary() {
  console.log('\n');
  console.log(`${COLORS.bright}${COLORS.green}=== Résumé des hooks Git configurés ====${COLORS.reset}`);
  console.log(`${COLORS.bright}Hook pre-commit:${COLORS.reset} ${path.relative(process.cwd(), PRE_COMMIT_HOOK)}`);
  console.log(`${COLORS.bright}Configuration lint-staged:${COLORS.reset} ${path.relative(process.cwd(), path.resolve(__dirname, '../.lintstagedrc'))}`);
  
  console.log('\n');
  console.log(`${COLORS.bright}${COLORS.magenta}Validation automatique avant chaque commit:${COLORS.reset}`);
  console.log(`  ${COLORS.cyan}● Fichiers TypeScript/JavaScript:${COLORS.reset} ESLint + Prettier`);
  console.log(`  ${COLORS.cyan}● Fichiers CSS/SCSS:${COLORS.reset} Prettier`);
  console.log(`  ${COLORS.cyan}● Fichiers JSON/Markdown:${COLORS.reset} Prettier`);
  
  console.log('\n');
  console.log(`${COLORS.bright}${COLORS.yellow}Note:${COLORS.reset} Vous pouvez contourner les hooks lors d'un commit en utilisant l'option ${COLORS.bright}--no-verify${COLORS.reset}`);
  console.log(`Par exemple: ${COLORS.bright}git commit -m "message" --no-verify${COLORS.reset}`);
  console.log('\n');
}

// Exécuter le script
setupGitHooks().catch(err => {
  console.error(`${COLORS.red}Erreur:${COLORS.reset}`, err);
  process.exit(1); 