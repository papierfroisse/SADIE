const fs = require('fs');
const path = require('path');
const { execSync } = require('child_process');

// Définition des chemins
const SRC_DIR = path.join(__dirname, '../src');
const REPORT_DIR = path.join(__dirname, '../reports');
const STATS_FILE = path.join(REPORT_DIR, 'code-stats.json');

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

console.log(`${colors.blue}==========================================${colors.reset}`);
console.log(`${colors.blue}   ANALYSE STATISTIQUE DU CODE SOURCE    ${colors.reset}`);
console.log(`${colors.blue}==========================================${colors.reset}`);

// Statistiques globales
const stats = {
  timestamp: new Date().toISOString(),
  summary: {
    totalFiles: 0,
    totalLines: 0,
    totalCode: 0,
    totalComments: 0,
    totalBlank: 0,
    averageFileSize: 0,
  },
  byExtension: {},
  byDirectory: {},
  largestFiles: [],
  mostComplexComponents: [],
};

// Extensions à analyser
const extensions = ['.js', '.jsx', '.ts', '.tsx', '.css', '.scss'];

// Fonction pour trouver tous les fichiers récursivement
function findFiles(dir, fileList = []) {
  const files = fs.readdirSync(dir);
  
  files.forEach(file => {
    const filePath = path.join(dir, file);
    
    if (fs.statSync(filePath).isDirectory()) {
      if (file !== 'node_modules' && file !== 'build' && !file.startsWith('.')) {
        findFiles(filePath, fileList);
      }
    } else {
      const ext = path.extname(file);
      if (extensions.includes(ext)) {
        fileList.push(filePath);
      }
    }
  });
  
  return fileList;
}

// Analyse des fichiers
console.log(`${colors.cyan}Recherche des fichiers à analyser...${colors.reset}`);
const files = findFiles(SRC_DIR);
console.log(`${colors.green}Trouvé ${files.length} fichiers à analyser.${colors.reset}`);

stats.summary.totalFiles = files.length;

// Analyser chaque fichier
console.log(`\n${colors.cyan}Analyse des fichiers en cours...${colors.reset}`);

files.forEach(filePath => {
  const content = fs.readFileSync(filePath, 'utf8');
  const ext = path.extname(filePath);
  const relativeDir = path.dirname(filePath).replace(SRC_DIR, '').substring(1);
  const directory = relativeDir || 'root';
  
  // Comptage des lignes
  const lines = content.split('\n');
  const totalLines = lines.length;
  
  // Estimation simple des lignes de code, commentaires et lignes vides
  let codeLines = 0;
  let commentLines = 0;
  let blankLines = 0;
  
  lines.forEach(line => {
    const trimmedLine = line.trim();
    
    if (trimmedLine === '') {
      blankLines++;
    } else if (trimmedLine.startsWith('//') || trimmedLine.startsWith('/*') || trimmedLine.endsWith('*/') || trimmedLine.startsWith('*')) {
      commentLines++;
    } else {
      codeLines++;
    }
  });
  
  // Ajouter aux statistiques globales
  stats.summary.totalLines += totalLines;
  stats.summary.totalCode += codeLines;
  stats.summary.totalComments += commentLines;
  stats.summary.totalBlank += blankLines;
  
  // Statistiques par extension
  if (!stats.byExtension[ext]) {
    stats.byExtension[ext] = {
      files: 0,
      lines: 0,
      code: 0,
      comments: 0,
      blank: 0,
    };
  }
  
  stats.byExtension[ext].files++;
  stats.byExtension[ext].lines += totalLines;
  stats.byExtension[ext].code += codeLines;
  stats.byExtension[ext].comments += commentLines;
  stats.byExtension[ext].blank += blankLines;
  
  // Statistiques par répertoire
  if (!stats.byDirectory[directory]) {
    stats.byDirectory[directory] = {
      files: 0,
      lines: 0,
      code: 0,
      comments: 0,
      blank: 0,
    };
  }
  
  stats.byDirectory[directory].files++;
  stats.byDirectory[directory].lines += totalLines;
  stats.byDirectory[directory].code += codeLines;
  stats.byDirectory[directory].comments += commentLines;
  stats.byDirectory[directory].blank += blankLines;
  
  // Collecter les plus gros fichiers
  stats.largestFiles.push({
    path: filePath.replace(SRC_DIR + path.sep, ''),
    lines: totalLines,
    code: codeLines,
    size: fs.statSync(filePath).size,
  });
  
  // Tentative d'estimation de la complexité pour les composants React
  if ((ext === '.jsx' || ext === '.tsx') && content.includes('React.') || content.includes('import React')) {
    const hooks = (content.match(/use[A-Z][a-zA-Z]+/g) || []).length;
    const effects = (content.match(/useEffect/g) || []).length;
    const states = (content.match(/useState/g) || []).length;
    const props = (content.match(/interface [A-Za-z]+Props/g) || []).length;
    
    const complexity = codeLines + hooks * 2 + effects * 3 + states * 2 + props;
    
    stats.mostComplexComponents.push({
      path: filePath.replace(SRC_DIR + path.sep, ''),
      complexity,
      lines: totalLines,
      hooks,
      effects,
      states,
    });
  }
});

// Finaliser les statistiques
stats.summary.averageFileSize = stats.summary.totalLines / stats.summary.totalFiles;

// Trier pour obtenir les N plus grands fichiers
stats.largestFiles.sort((a, b) => b.lines - a.lines);
stats.largestFiles = stats.largestFiles.slice(0, 10);

// Trier pour obtenir les N composants les plus complexes
stats.mostComplexComponents.sort((a, b) => b.complexity - a.complexity);
stats.mostComplexComponents = stats.mostComplexComponents.slice(0, 10);

// Calculer les ratios de commentaires et de code
const commentRatio = (stats.summary.totalComments / stats.summary.totalCode * 100).toFixed(2);

// Écrire les statistiques dans un fichier JSON
fs.writeFileSync(STATS_FILE, JSON.stringify(stats, null, 2));

// Afficher un résumé des statistiques
console.log(`\n${colors.blue}==========================================${colors.reset}`);
console.log(`${colors.blue}               RÉSUMÉ                     ${colors.reset}`);
console.log(`${colors.blue}==========================================${colors.reset}`);

console.log(`${colors.white}• Nombre total de fichiers: ${colors.cyan}${stats.summary.totalFiles}${colors.reset}`);
console.log(`${colors.white}• Nombre total de lignes: ${colors.cyan}${stats.summary.totalLines}${colors.reset}`);
console.log(`${colors.white}• Lignes de code: ${colors.cyan}${stats.summary.totalCode}${colors.reset}`);
console.log(`${colors.white}• Lignes de commentaires: ${colors.cyan}${stats.summary.totalComments} ${colors.reset}(${commentRatio}% du code)`);
console.log(`${colors.white}• Lignes vides: ${colors.cyan}${stats.summary.totalBlank}${colors.reset}`);
console.log(`${colors.white}• Taille moyenne des fichiers: ${colors.cyan}${Math.round(stats.summary.averageFileSize)} lignes${colors.reset}`);

// Afficher les statistiques par extension
console.log(`\n${colors.yellow}Statistiques par extension:${colors.reset}`);
Object.entries(stats.byExtension).forEach(([ext, data]) => {
  console.log(`${colors.white}• ${ext}: ${colors.cyan}${data.files} fichiers, ${data.lines} lignes (${data.code} code, ${data.comments} commentaires)${colors.reset}`);
});

// Afficher les 5 plus gros fichiers
console.log(`\n${colors.yellow}Les 5 plus gros fichiers:${colors.reset}`);
stats.largestFiles.slice(0, 5).forEach((file, index) => {
  console.log(`${colors.white}${index + 1}. ${file.path}: ${colors.cyan}${file.lines} lignes (${(file.size / 1024).toFixed(2)} KB)${colors.reset}`);
});

// Afficher les 5 composants les plus complexes
if (stats.mostComplexComponents.length > 0) {
  console.log(`\n${colors.yellow}Les 5 composants React les plus complexes:${colors.reset}`);
  stats.mostComplexComponents.slice(0, 5).forEach((comp, index) => {
    console.log(`${colors.white}${index + 1}. ${comp.path}: ${colors.cyan}complexité ${comp.complexity}, ${comp.hooks} hooks, ${comp.effects} effets${colors.reset}`);
  });
}

console.log(`\n${colors.green}Rapport complet sauvegardé dans: ${colors.reset}${colors.white}${STATS_FILE}${colors.reset}`);

// Tentative d'afficher une tendance de l'évolution du code (nécessite git)
try {
  console.log(`\n${colors.yellow}Évolution du code (basée sur git):${colors.reset}`);
  
  const gitStats = execSync('git log --author="$(git config user.name)" --pretty=tformat: --numstat | awk \'{inserted+=$1; deleted+=$2} END {print inserted, deleted}\'', { cwd: SRC_DIR, encoding: 'utf8' }).trim().split(' ');
  
  if (gitStats.length === 2) {
    const [inserted, deleted] = gitStats.map(Number);
    console.log(`${colors.white}• Lignes ajoutées historiquement: ${colors.green}${inserted}${colors.reset}`);
    console.log(`${colors.white}• Lignes supprimées historiquement: ${colors.red}${deleted}${colors.reset}`);
    console.log(`${colors.white}• Bilan net: ${inserted - deleted > 0 ? colors.green : colors.red}${inserted - deleted}${colors.reset}`);
  }
} catch (error) {
  console.log(`${colors.white}• Statistiques git non disponibles ou erreur: ${error.message}${colors.reset}`);
}

console.log(`\n${colors.blue}==========================================${colors.reset}`); 