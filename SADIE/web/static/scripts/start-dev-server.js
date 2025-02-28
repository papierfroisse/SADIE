/**
 * Script pour démarrer le serveur de développement avec une meilleure gestion des erreurs
 * Ce script est utilisé dans l'environnement Docker pour démarrer React avec plus de stabilité
 */

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

// Configuration
const MAX_RETRIES = 3;
const RETRY_DELAY = 5000; // 5 secondes
const LOG_FILE = path.join(__dirname, '../logs/dev-server.log');

// Créer le répertoire de logs s'il n'existe pas
const logDir = path.dirname(LOG_FILE);
if (!fs.existsSync(logDir)) {
  fs.mkdirSync(logDir, { recursive: true });
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

// Fonction pour logger les messages
function log(message, type = 'info') {
  const timestamp = new Date().toISOString();
  let coloredMessage = '';
  
  switch (type) {
    case 'error':
      coloredMessage = `${COLORS.red}[ERREUR]${COLORS.reset} ${message}`;
      break;
    case 'warning':
      coloredMessage = `${COLORS.yellow}[ATTENTION]${COLORS.reset} ${message}`;
      break;
    case 'success':
      coloredMessage = `${COLORS.green}[SUCCÈS]${COLORS.reset} ${message}`;
      break;
    default:
      coloredMessage = `${COLORS.blue}[INFO]${COLORS.reset} ${message}`;
  }
  
  console.log(`${timestamp} - ${coloredMessage}`);
  
  // Écrire dans le fichier de log
  fs.appendFileSync(LOG_FILE, `${timestamp} - [${type.toUpperCase()}] ${message}\n`);
}

// Fonction pour démarrer le serveur React
function startReactServer(retryCount = 0) {
  if (retryCount >= MAX_RETRIES) {
    log(`Nombre maximum de tentatives atteint (${MAX_RETRIES}). Arrêt du script.`, 'error');
    process.exit(1);
  }
  
  log(`Démarrage du serveur de développement React (tentative ${retryCount + 1}/${MAX_RETRIES})...`);
  
  // Configurer les variables d'environnement
  const env = {
    ...process.env,
    GENERATE_SOURCEMAP: 'false',
    BROWSER: 'none',
    CI: 'false',
  };
  
  // Démarrer le processus React
  const reactProcess = spawn('node', [
    '--max-old-space-size=8192',
    path.join(__dirname, '../node_modules/.bin/react-scripts'),
    'start'
  ], {
    env,
    stdio: 'pipe',
    shell: true
  });
  
  // Gérer les sorties
  reactProcess.stdout.on('data', (data) => {
    const output = data.toString().trim();
    console.log(output);
    
    // Détecter le démarrage réussi
    if (output.includes('Compiled successfully') || output.includes('Starting the development server')) {
      log('Le serveur de développement React a démarré avec succès', 'success');
    }
  });
  
  reactProcess.stderr.on('data', (data) => {
    const errorOutput = data.toString().trim();
    
    // Ignorer certains avertissements courants
    if (errorOutput.includes('DeprecationWarning') || 
        errorOutput.includes('Warning:') ||
        errorOutput.includes('Compiled with warnings')) {
      console.warn(errorOutput);
    } else {
      log(errorOutput, 'error');
    }
  });
  
  // Gérer les erreurs et les fins de processus
  reactProcess.on('error', (error) => {
    log(`Erreur lors du démarrage du serveur React: ${error.message}`, 'error');
    retryServerStart(retryCount);
  });
  
  reactProcess.on('exit', (code, signal) => {
    if (code !== 0 || signal) {
      log(`Le serveur React s'est arrêté avec le code ${code || 'inconnu'} (signal: ${signal || 'aucun'})`, 'warning');
      retryServerStart(retryCount);
    } else {
      log('Le serveur React s\'est arrêté normalement', 'info');
    }
  });
  
  // Gérer les arrêts du script
  process.on('SIGINT', () => {
    log('Signal d\'interruption reçu. Arrêt du serveur React...', 'warning');
    reactProcess.kill('SIGINT');
    process.exit(0);
  });
  
  process.on('SIGTERM', () => {
    log('Signal de terminaison reçu. Arrêt du serveur React...', 'warning');
    reactProcess.kill('SIGTERM');
    process.exit(0);
  });
  
  return reactProcess;
}

// Fonction pour réessayer de démarrer le serveur
function retryServerStart(retryCount) {
  log(`Redémarrage du serveur dans ${RETRY_DELAY / 1000} secondes...`, 'warning');
  
  setTimeout(() => {
    startReactServer(retryCount + 1);
  }, RETRY_DELAY);
}

// Affichez le banner
console.log(`${COLORS.bright}${COLORS.magenta}
=============================================
  SADIE - Serveur de Développement React
=============================================
${COLORS.reset}`);

// Démarrer le serveur React
startReactServer(); 